import os.path
import math  # inf
import numpy as np

from deepfly.utils_ramdya_lab import find_default_camera_ordering
from deepfly.GUI.CameraNetwork import CameraNetwork
from deepfly.GUI.Config import config
from deepfly.GUI.util.os_util import write_camera_order, read_camera_order, read_calib, get_max_img_id
from deepfly.GUI.util.optim_util import energy_drosoph
from deepfly.pose2d import ArgParse
from deepfly.pose2d.drosophila import main as pose2d_main


class Core:
    def __init__(self, input_folder, num_images_max):
        self.input_folder = input_folder
        self.output_folder = os.path.join(self.input_folder, 'df3d/')
        
        self.num_images_max = num_images_max or math.inf
        max_img_id = get_max_img_id(self.input_folder)
        self.num_images = min(self.num_images_max, max_img_id + 1)
        self.max_img_id = self.num_images - 1

        self.setup_camera_ordering()
        self.set_cameras()
        

    @property
    def input_folder(self): 
        return self._input_folder


    @input_folder.setter 
    def input_folder(self, value): 
        value = os.path.abspath(value)
        value = value.rstrip('/')
        assert os.path.isdir(value), f'Not a directory {value}'
        self._input_folder = value 


    @property
    def output_folder(self): 
        return self._output_folder


    @output_folder.setter 
    def output_folder(self, value): 
        os.makedirs(value, exist_ok=True)
        value = os.path.abspath(value)
        value = value.rstrip('/')
        assert os.path.isdir(value), f'Not a directory {value}'
        self._output_folder = value 



    def setup_camera_ordering(self):
        default = find_default_camera_ordering(self.input_folder)
        if default is not None:  # np.arrays don't evaluate to bool
            write_camera_order(self.output_folder, default)
        self.cidread2cid, self.cid2cidread = read_camera_order(self.output_folder)


    def update_camera_ordering(self, cidread2cid):
        if cidread2cid is None:
            return False

        if len(cidread2cid) != config["num_cameras"]:
            print(f"Cannot rename images as there are no {config['num_cameras']} values")
            return False

        print("Camera order {}".format(cidread2cid))
        write_camera_order(self.output_folder, cidread2cid)
        self.cidread2cid, self.cid2cidread = read_camera_order(self.output_folder)
        self.camNetAll.set_cid2cidread(self.cid2cidread)
        return True


    def set_cameras(self):
        calib = read_calib(self.output_folder)
        self.camNetAll = CameraNetwork(
            image_folder=self.input_folder,
            output_folder=self.output_folder,
            cam_id_list=range(config["num_cameras"]),
            cid2cidread=self.cid2cidread,
            num_images=self.num_images,
            calibration=calib,
            num_joints=config["skeleton"].num_joints,
            heatmap_shape=config["heatmap_shape"],
        )
        self.camNetLeft = CameraNetwork(
            image_folder=self.input_folder,
            output_folder=self.output_folder,
            cam_id_list=config["left_cameras"],
            num_images=self.num_images,
            calibration=calib,
            num_joints=config["skeleton"].num_joints,
            cid2cidread=[self.cid2cidread[cid] for cid in config["left_cameras"]],
            heatmap_shape=config["heatmap_shape"],
            cam_list=[cam for cam in self.camNetAll if cam.cam_id in config["left_cameras"]],
        )
        self.camNetRight = CameraNetwork(
            image_folder=self.input_folder,
            output_folder=self.output_folder,
            cam_id_list=config["right_cameras"],
            num_images=self.num_images,
            calibration=calib,
            num_joints=config["skeleton"].num_joints,
            cid2cidread=[self.cid2cidread[cid] for cid in config["right_cameras"]],
            heatmap_shape=config["heatmap_shape"],
            cam_list=[self.camNetAll[cam_id] for cam_id in config["right_cameras"]],
        )

        self.camNetLeft.bone_param = config["bone_param"]
        self.camNetRight.bone_param = config["bone_param"]
        calib = read_calib(config["calib_fine"])
        self.camNetAll.load_network(calib)


    def pose2d_estimation(self):
        parser = ArgParse.create_parser()
        args, _ = parser.parse_known_args()
        args.checkpoint = False
        args.unlabeled = self.input_folder
        args.resume = config["resume"]
        args.stacks = config["num_stacks"]
        args.test_batch = config["batch_size"]
        args.img_res = [config["heatmap_shape"][0] * 4, config["heatmap_shape"][1] * 4]
        args.hm_res = config["heatmap_shape"]
        args.num_classes = config["num_predict"]
        args.max_img_id = self.max_img_id

        pose2d_main(args)   # will write output files in output directory
        self.set_cameras()  # makes sure cameras use the latest heatmaps and predictions


    def get_joint_reprojection_error(self, img_id, joint_id, camNet):
        visible_cameras = [
            cam
            for cam in camNet
            if config["skeleton"].camera_see_joint(cam.cam_id, joint_id)
        ]
        if len(visible_cameras) >= 2:
            pts = np.array(
                [cam.points2d[img_id, joint_id, :] for cam in visible_cameras]
            )
            _, err_proj, _, _ = energy_drosoph(
                visible_cameras, img_id, joint_id, pts / [960, 480]
            )
        else:
            err_proj = 0

        return err_proj


    def next_error(self, img_id):
        return min(
            self.next_error_cam(img_id, self.camNetLeft),
            self.next_error_cam(img_id, self.camNetRight),
        )


    def next_error_cam(self, img_id, camNet):
        for img_id in range(img_id + 1, self.num_images):
            for joint_id in range(config["skeleton"].num_joints):
                if joint_id not in config["skeleton"].pictorial_joint_list:
                    continue
                err_proj = self.get_joint_reprojection_error(img_id, joint_id, camNet)
                if err_proj > config["reproj_thr"][joint_id]:
                    print("{} {} {}".format(img_id, joint_id, err_proj))
                    return img_id

        return self.max_img_id


    def prev_error(self, img_id):
        return max(
            self.prev_error_cam(img_id, self.camNetLeft),
            self.prev_error_cam(img_id, self.camNetRight),
        )


    def prev_error_cam(self, curr_img_id, camNet):
        for img_id in range(curr_img_id - 1, 0, -1):
            for joint_id in range(config["skeleton"].num_joints):
                if joint_id not in config["skeleton"].pictorial_joint_list:
                    continue
                err_proj = self.get_joint_reprojection_error(img_id, joint_id, camNet)
                if err_proj > config["reproj_thr"][joint_id]:
                    print("{} {} {}".format(img_id, joint_id, err_proj))
                    return img_id

        return 0

