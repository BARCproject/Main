#!/usr/bin/env python
"""
    File name: state_estimator.py
    Author: Shuqi Xu
    Email: shuqixu@kth.se
    Python Version: 2.7.12
"""
# ---------------------------------------------------------------------------
# Licensing Information: You are free to use or extend these projects for
# education or reserach purposes provided that (1) you retain this notice
# and (2) you provide clear attribution to UC Berkeley, including a link
# to http://barc-project.com
#
# Attibution Information: The barc project ROS code-base was developed
# at UC Berkeley in the Model Predictive Control (MPC) lab by Jon Gonzales
# (jon.gonzales@berkeley.edu). The cloud services integation with ROS was developed
# by Kiet Lam  (kiet.lam@berkeley.edu). The web-server app Dator was
# based on an open source project by Bruce Wootton
# ---------------------------------------------------------------------------
import sys
sys.path.append(sys.path[0]+'/ControllersObject')
sys.path.append(sys.path[0]+'/Utilities')
import rospy
from barc.msg import ECU, pos_info, Vel_est
from sensor_msgs.msg import Imu
from marvelmind_nav.msg import hedge_imu_fusion, hedge_pos
from std_msgs.msg import Header
from numpy import eye, zeros, diag, tan, cos, sin, vstack, linalg, pi
from numpy import ones, polyval, size, dot, add
from scipy.linalg import inv, cholesky
from tf import transformations
import math
import numpy as np
import os
import pdb

def main():
    # node initialization
    rospy.init_node("state_estimation")

    node_name = rospy.get_name()
    a_delay     = rospy.get_param(node_name + "/delay_a")
    df_delay    = rospy.get_param(node_name + "/delay_df")
    loop_rate   = 50.0
   
    # low velocity
    Q = eye(8)
    Q[0,0] = 0.01    # x
    Q[1,1] = 0.01    # y
    Q[2,2] = 0.5     # vx
    Q[3,3] = 0.5     # vy
    Q[4,4] = 5.0     # ax
    Q[5,5] = 1.0     # ay 
    Q[6,6] = 0.01    # psi
    Q[7,7] = 10.0    # psiDot
    R = eye(7)
    R[0,0] = 0.5   # x
    R[1,1] = 0.5   # y
    R[2,2] = 0.1      # vx
    R[3,3] = 0.01     # ax 
    R[4,4] = 10.0     # ay 
    R[5,5] = 20.0     # psiDot
    R[6,6] = 0.001    # vy
    thReset = 1.4

    Q_1 = eye(8)
    Q_1[0,0] = 0.01    # x
    Q_1[1,1] = 0.01    # y
    Q_1[2,2] = 0.5     # vx
    Q_1[3,3] = 0.5     # vy
    Q_1[4,4] = 1.0     # ax
    Q_1[5,5] = 1.0     # ay 
    Q_1[6,6] = 0.01    # psi
    Q_1[7,7] = 10.0    # psiDot
    R_1 = eye(7)
    R_1[0,0] = 5.0     # x
    R_1[1,1] = 5.0     # y
    R_1[2,2] = 1.0     # vx
    R_1[3,3] = 0.0001  # ax 
    R_1[4,4] = 10.0    # ay 
    R_1[5,5] = 20.0    # psiDot
    R_1[6,6] = 0.001   # vy
    thReset_1 = 0.4

    # high velocity
    Q_noVy = eye(8)
    Q_noVy[0,0] = 0.01 # x
    Q_noVy[1,1] = 0.01 # y
    Q_noVy[2,2] = 0.01 # vx
    Q_noVy[3,3] = 0.01 # vy
    Q_noVy[4,4] = 1.0 # ax
    Q_noVy[5,5] = 1.0 # ay
    Q_noVy[6,6] = 10.0 # psi
    Q_noVy[7,7] = 10.0 # psidot
    # Q[8,8] = 0.0 # psiDot in the model
    R_noVy = eye(6)
    R_noVy[0,0] = 5.0   # x
    R_noVy[1,1] = 5.0   # y
    R_noVy[2,2] = 0.1   # vx
    R_noVy[3,3] = 10.0   # ax
    R_noVy[4,4] = 30.0   # ay
    R_noVy[5,5] = 0.1    # psiDot
    thReset_noVy = 0.8

    node_name = rospy.get_name()
    if node_name[-1] == "2":
        # Agent 2 Tuning
        Q_dyn = eye(8)
        Q_dyn[0,0] = 0.01    # x
        Q_dyn[1,1] = 0.01    # y
        Q_dyn[2,2] = 0.01     # vx
        Q_dyn[3,3] = 0.1 # pretty good # 0.01     # vy
        Q_dyn[4,4] = 1.0 * 1.0     # ax
        Q_dyn[5,5] = 1.0 * 1.0     # ay 
        Q_dyn[6,6] = 0.0001 # 0.05 # 0.01 # 0.1 * 1.0 # 0.01 # not bad, but drifting# 20.0    # psi
        Q_dyn[7,7] = 0.1 * 0.1 * 1.0    # psiDot
        R_dyn = eye(6)
        R_dyn[0,0] = 7.0 # 0.2 * 5.0 * 10.0   # x
        R_dyn[1,1] = 7.0 # 0.2 * 5.0 * 10.0   # y
        R_dyn[2,2] = 1.0 * 0.1      # vx
        R_dyn[3,3] = 0.5 * 10.0     # ax 
        R_dyn[4,4] = 1.0 * 10.0     # ay 
        R_dyn[5,5] = 0.1     # psiDot
        thReset = 10000.0
    else:
        # Agent 1 Tuning
        Q_dyn = eye(8)
        Q_dyn[0,0] = 0.01    # x
        Q_dyn[1,1] = 0.01    # y
        Q_dyn[2,2] = 0.01     # vx
        Q_dyn[3,3] = 0.1 # pretty good # 0.01     # vy
        Q_dyn[4,4] = 1.0 * 1.0     # ax
        Q_dyn[5,5] = 1.0 * 1.0     # ay 
        Q_dyn[6,6] = 0.0005 # 0.05 # 0.01 # 0.1 * 1.0 # 0.01 # not bad, but drifting# 20.0    # psi
        Q_dyn[7,7] = 0.1 * 0.1 * 1.0    # psiDot
        R_dyn = eye(6)
        R_dyn[0,0] = 7.0 # 0.2 * 5.0 * 10.0   # x
        R_dyn[1,1] = 7.0 # 0.2 * 5.0 * 10.0   # y
        R_dyn[2,2] = 1.0 * 0.1      # vx
        R_dyn[3,3] = 0.5 * 10.0     # ax 
        R_dyn[4,4] = 1.0 * 10.0     # ay 
        R_dyn[5,5] = 0.1     # psiDot
        thReset = 10000.0


    # Q_dyn = eye(8)
    # Q_dyn[0,0] = 0.01    # x
    # Q_dyn[1,1] = 0.01    # y
    # Q_dyn[2,2] = 0.01     # vx
    # Q_dyn[3,3] = 0.01 # 0.1 # pretty good # 0.01     # vy
    # Q_dyn[4,4] = 1.0 * 1.0     # ax
    # Q_dyn[5,5] = 1.0 * 1.0     # ay 
    # Q_dyn[6,6] = 0.1 * 1.0 # 0.01 # not bad, but drifting# 20.0    # psi
    # Q_dyn[7,7] = 0.1 * 0.1 * 1.0    # psiDot
    # R_dyn = eye(6)
    # R_dyn[0,0] = 0.2 * 5.0 * 10.0   # x
    # R_dyn[1,1] = 0.2 * 5.0 * 10.0   # y
    # R_dyn[2,2] = 1.0 * 0.1      # vx
    # R_dyn[3,3] = 0.5 * 10.0     # ax 
    # R_dyn[4,4] = 1.0 * 10.0     # ay 
    # R_dyn[5,5] = 0.1     # psiDot
    # thReset = 10000.0

    twoEstimators = False
    switchEstimators = False



    t0 = rospy.get_rostime().to_sec()
    imu = ImuClass(t0)
    gps = GpsClass(t0)
    enc = EncClass(t0)
    ecu = EcuClass(t0)

    est     = Estimator(t0,loop_rate,a_delay,df_delay,Q,  R,   thReset)
    est_1   = Estimator(t0,loop_rate,a_delay,df_delay,Q_1,R_1, thReset_1)
    estNoVy = EstimatorNoVy(t0,loop_rate,a_delay,df_delay,Q_noVy,R_noVy, thReset_noVy)

    est_dyn  = Estimator(t0,loop_rate,a_delay,df_delay,Q_dyn,  R_dyn,   thReset, dynamic_model=True)

    estMsg = pos_info()
    
    saved_x_est      = []
    saved_y_est      = []
    saved_vx_est     = []
    saved_vy_est     = []
    saved_psi_est    = []
    saved_psiDot_est = []
    saved_ax_est     = []
    saved_ay_est     = []

    while not rospy.is_shutdown():
        
        est.estimateState(imu,gps,enc,ecu,est.ekf)
        if est.vx_est > 0.5:
            est_dyn.estimateState(imu, gps, enc, ecu, est_dyn.ekf)

        if twoEstimators == True:          
            est_1.estimateState(imu,gps,enc,ecu,est_1.ekf)

        if switchEstimators == True:
            estNoVy.estimateState(imu, gps, enc, ecu, estNoVy.ekf)
        
        estMsg.header.stamp = rospy.get_rostime()

        if est.vx_est > 0.5:
            est.z = est_dyn.z
            # print "DYNAMIC ESTIMATOR"
            estMsg.v        = np.sqrt(est_dyn.vx_est**2 + est_dyn.vy_est**2)
            estMsg.x        = est_dyn.x_est 
            estMsg.y        = est_dyn.y_est
            estMsg.v_x      = est_dyn.vx_est 
            estMsg.v_y      = est_dyn.vy_est
            estMsg.psi      = est_dyn.yaw_est
            estMsg.psiDot   = est_dyn.psiDot_est
            estMsg.a_x      = est_dyn.ax_est
            estMsg.a_y      = est_dyn.ay_est
            estMsg.u_a      = ecu.a
            estMsg.u_df     = ecu.df
        else:
            est_dyn.z = est.z
            # print "KINEMATIC ESTIMATOR"
            estMsg.v        = np.sqrt(est.vx_est**2 + est.vy_est**2)
            estMsg.x        = est.x_est 
            estMsg.y        = est.y_est
            estMsg.v_x      = est.vx_est 
            estMsg.v_y      = est.vy_est
            estMsg.psi      = est.yaw_est
            estMsg.psiDot   = est.psiDot_est
            estMsg.a_x      = est.ax_est
            estMsg.a_y      = est.ay_est
            estMsg.u_a      = ecu.a
            estMsg.u_df     = ecu.df

        """
        if switchEstimators == True:
            if (est.vx_est + 0.0 * est.psiDot_est) > 1.3 or (np.abs(est.psiDot_est) > 2.0):
                print "HIGH VELOCITY ESTIMATOR KICKED IN"
                estMsg.v        = np.sqrt(estNoVy.vx_est**2 + estNoVy.vy_est**2)
                estMsg.x        = estNoVy.x_est 
                estMsg.y        = estNoVy.y_est
                estMsg.v_x      = estNoVy.vx_est 
                estMsg.v_y      = estNoVy.vy_est
                estMsg.psi      = estNoVy.yaw_est
                estMsg.psiDot   = estNoVy.psiDot_est
                estMsg.a_x      = estNoVy.ax_est
                estMsg.a_y      = estNoVy.ay_est
                estMsg.u_a      = ecu.a
                estMsg.u_df     = ecu.df
            else:
                estMsg.v        = np.sqrt(est.vx_est**2 + est.vy_est**2)
                estMsg.x        = est.x_est 
                estMsg.y        = est.y_est
                estMsg.v_x      = est.vx_est 
                estMsg.v_y      = est.vy_est
                estMsg.psi      = est.yaw_est
                estMsg.psiDot   = est.psiDot_est
                estMsg.a_x      = est.ax_est
                estMsg.a_y      = est.ay_est
                estMsg.u_a      = ecu.a
                estMsg.u_df     = ecu.df
        elif twoEstimators == True:    
            estMsg.v        = np.sqrt(est_1.vx_est**2 + est_1.vy_est**2)
            estMsg.x        = est.x_est 
            estMsg.y        = est.y_est
            estMsg.v_x      = est_1.vx_est 
            estMsg.v_y      = est_1.vy_est
            estMsg.psi      = est_1.yaw_est
            estMsg.psiDot   = est_1.psiDot_est
            estMsg.a_x      = est_1.ax_est
            estMsg.a_y      = est_1.ay_est
            estMsg.u_a      = ecu.a
            estMsg.u_df     = ecu.df
        else:
            estMsg.v        = np.sqrt(est.vx_est**2 + est.vy_est**2)
            estMsg.x        = est.x_est 
            estMsg.y        = est.y_est
            estMsg.v_x      = est.vx_est 
            estMsg.v_y      = est.vy_est
            estMsg.psi      = est.yaw_est
            estMsg.psiDot   = est.psiDot_est
            estMsg.a_x      = est.ax_est
            estMsg.a_y      = est.ay_est
            estMsg.u_a      = ecu.a
            estMsg.u_df     = ecu.df
        """

        est.state_pub_pos.publish(estMsg)

        # Save estimator output.
        # NEED TO DO IT HERE AS THERE ARE MULTIPLE ESTIMATOR RUNNING IN PARALLEL
        saved_x_est.append(estMsg.x)
        saved_y_est.append(estMsg.y)
        saved_vx_est.append(estMsg.v_x)
        saved_vy_est.append(estMsg.v_y)
        saved_psi_est.append(estMsg.psi)
        saved_psiDot_est.append(estMsg.psiDot)
        saved_ax_est.append(estMsg.a_x)
        saved_ay_est.append(estMsg.a_y)

        est.rate.sleep()

    homedir = os.path.expanduser("~")
    pathSave = os.path.join(homedir,"barc_data/estimator_output.npz")
    np.savez(pathSave,yaw_est_his       = saved_psi_est,
                      psiDot_est_his    = saved_psiDot_est,
                      x_est_his         = saved_x_est,
                      y_est_his         = saved_y_est,
                      vx_est_his        = saved_vx_est,
                      vy_est_his        = saved_vy_est,
                      ax_est_his        = saved_ax_est,
                      ay_est_his        = saved_ay_est,
                      gps_time          = est.gps_time,
                      imu_time          = est.imu_time,
                      enc_time          = est.enc_time,
                      inp_x_his         = est.x_his,
                      inp_y_his         = est.y_his,
                      inp_v_meas_his    = est.v_meas_his,
                      inp_ax_his        = est.ax_his,
                      inp_ay_his        = est.ay_his,
                      inp_psiDot_his    = est.psiDot_his,
                      inp_a_his         = est.inp_a_his,
                      inp_df_his        = est.inp_df_his)

    pathSave = os.path.join(homedir,"barc_data/estimator_imu.npz")
    np.savez(pathSave,psiDot_his    = imu.psiDot_his,
                      roll_his      = imu.roll_his,
                      pitch_his     = imu.pitch_his,
                      yaw_his       = imu.yaw_his,
                      ax_his        = imu.ax_his,
                      ay_his        = imu.ay_his,
                      imu_time      = imu.time_his)

    pathSave = os.path.join(homedir,"barc_data/estimator_gps.npz")
    np.savez(pathSave,x_his         = gps.x_his,
                      y_his         = gps.y_his,
                      gps_time      = gps.time_his)

    pathSave = os.path.join(homedir,"barc_data/estimator_enc.npz")
    np.savez(pathSave,v_fl_his          = enc.v_fl_his,
                      v_fr_his          = enc.v_fr_his,
                      v_rl_his          = enc.v_rl_his,
                      v_rr_his          = enc.v_rr_his,
                      enc_time          = enc.time_his)

    pathSave = os.path.join(homedir,"barc_data/estimator_ecu.npz")
    np.savez(pathSave,a_his         = ecu.a_his,
                      df_his        = ecu.df_his,
                      ecu_time      = ecu.time_his)

    print "Finishing saveing state estimation data"

class Estimator(object):
    """ Object collecting  estimated state data
    Attributes:
        Estimated states:
            1.x_est     2.y_est
            3.vx_est    4.vy_est        5.v_est
            6.ax_est    7.ay_est
            8.yaw_est   9.psiDot_est    10.psiDrift_est
        Estimated states history:
            1.x_est_his     2.y_est_his
            3.vx_est_his    4.vy_est_his        5.v_est_his
            6.ax_est_his    7.ay_est_his
            8.yaw_est_his   9.psiDot_est_his    10.psiDrift_est_his
        Time stamp
            1.t0 2.time_his 3.curr_time
    Methods:
        stateEstimate(imu,gps,enc,ecu):
            Estimate current state from sensor data
        ekf(y,u):
            Extended Kalman filter
        ukf(y,u):
            Unscented Kalman filter
        numerical_jac(func,x,u):
            Calculate jacobian numerically
        f(x,u):
            System prediction model
        h(x,u):
            System measurement model
    """

    def __init__(self,t0,loop_rate,a_delay,df_delay,Q,R,thReset,dynamic_model=False):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """
        self.dynamic_model = dynamic_model

        self.l_f = 0.125
        self.l_r = 0.125
        self.I_z = 0.24

        node_name = rospy.get_name()
        if node_name[-1] == "2":
            self.front_corner_stiffness = 13.03
            self.rear_corner_stiffness = 10.06
            self.mass = 1.75
        else: 
            self.front_corner_stiffness = 12.38
            self.rear_corner_stiffness = 9.6
            self.mass = 2.0

        self.thReset = thReset

        dt          = 1.0 / loop_rate
        self.rate   = rospy.Rate(loop_rate)
        L_f         = rospy.get_param("L_a")       # distance from CoG to front axel
        L_r         = rospy.get_param("L_b")       # distance from CoG to rear axel
        self.vhMdl  = (L_f, L_r)
        self.Q      = Q
        self.R      = R
        self.P      = np.eye(np.size(Q,0)) # initializationtial covariance matrix
        self.z      = np.zeros(np.size(Q,0)) # initial state mean
        if dynamic_model:
            self.z[2] =  0.1
        self.dt     = dt
        self.a_delay        = a_delay
        self.df_delay       = df_delay
        self.a_his          = [0.0]*int(a_delay/dt)
        self.df_his         = [0.0]*int(df_delay/dt)

        self.state_pub_pos  = rospy.Publisher('pos_info', pos_info, queue_size=1)
        self.t0             = t0

        self.x_est          = 0.0
        self.y_est          = 0.0
        self.vx_est         = 0.0
        self.vy_est         = 0.0
        self.v_est          = 0.0
        self.ax_est         = 0.0
        self.ay_est         = 0.0
        self.yaw_est        = 0.0
        self.psiDot_est     = 0.0
        self.psiDrift_est   = 0.0
        self.curr_time      = rospy.get_rostime().to_sec()

        self.x_est_his          = []
        self.y_est_his          = []
        self.vx_est_his         = []
        self.vy_est_his         = []
        self.v_est_his          = []
        self.ax_est_his         = []
        self.ay_est_his         = []
        self.yaw_est_his        = []
        self.psiDot_est_his     = []
        self.time_his           = []

        # SAVE THE measurement/input SEQUENCE USED BY KF
        self.x_his      = []
        self.y_his      = []
        self.v_meas_his = []
        self.ax_his     = []
        self.ay_his     = []
        self.psiDot_his = []
        self.inp_a_his  = []
        self.inp_df_his = []

        self.gps_time = []
        self.enc_time = []
        self.imu_time = []

        self.oldGPS_x = 0.0
        self.oldGPS_y = 0.0

    # ecu command update
    def estimateState(self,imu,gps,enc,ecu,KF):
        """Do extended Kalman filter to estimate states"""
        self.curr_time = rospy.get_rostime().to_sec()

        self.a_his.append(ecu.a)
        self.df_his.append(ecu.df)
        u = [self.a_his.pop(0), self.df_his.pop(0)]
        # u = [ecu.a, self.df_his.pop(0)]
        
        bta = 0.5 * u[1]
        dist   = np.sqrt(( self.x_est - gps.x )**2 + ( self.y_est - gps.y )**2)

        """
        if vx_est > 0.5:
            self.dynamic_model = True
        else: 
            self.dynamic_model = False
        """

        # if ( dist >= 1 ) or ( (gps.x == self.oldGPS_x) and (gps.x == self.oldGPS_y) ):
        # if ( (gps.x == self.oldGPS_x) and (gps.x == self.oldGPS_y) ):
        if self.dynamic_model:
            modeGPS = True
            y = np.array([gps.x,        # x
                          gps.y,        # y
                          enc.v_meas,   # v_x
                          imu.ax,       # a_x
                          imu.ay,       # a_y
                          imu.psiDot])  # psi_dot
        elif 0 == 1:
            modeGPS = False
            y = np.array([enc.v_meas, imu.ax, imu.ay, imu.psiDot, bta * enc.v_meas])
        else:
            modeGPS = True
            y = np.array([gps.x, gps.y, enc.v_meas, imu.ax, imu.ay, imu.psiDot, bta * enc.v_meas])


        self.oldGPS_x = gps.x
        self.oldGPS_y = gps.y

        if np.abs(imu.psiDot) < self.thReset and not self.dynamic_model:
            self.z[3] = 0

        KF(y,u, modeGPS)


        # SAVE THE measurement/input SEQUENCE USED BY KF
        self.x_his.append(gps.x)
        self.y_his.append(gps.y)
        self.v_meas_his.append(enc.v_meas)
        self.ax_his.append(imu.ax)
        self.ay_his.append(imu.ay)
        self.psiDot_his.append(imu.psiDot)
        self.inp_a_his.append(u[0])
        self.inp_df_his.append(u[1])

        self.gps_time.append(gps.curr_time)
        self.imu_time.append(imu.curr_time)
        self.enc_time.append(enc.curr_time)
        # SAVE output KF given the above measurements
        self.saveHistory()

    def ekf(self, y, u, modeGPS):
        """
        EKF   Extended Kalman Filter for nonlinear dynamic systems
        ekf(f,mx,P,h,z,Q,R) returns state estimate, x and state covariance, P 
        for nonlinear dynamic system:
                  x_k+1 = f(x_k) + w_k
                  y_k   = h(x_k) + v_k
        where w ~ N(0,Q) meaning w is gaussian noise with covariance Q
              v ~ N(0,R) meaning v is gaussian noise with covariance R
        Inputs:    f: function handle for f(x)
                   z_EKF: "a priori" state estimate
                   P: "a priori" estimated state covariance
                   h: fanction handle for h(x)
                   y: current measurement
                   Q: process noise covariance 
                   R: measurement noise covariance
                   args: additional arguments to f(x, *args)
        Output:    mx_kp1: "a posteriori" state estimate
                   P_kp1: "a posteriori" state covariance
                   
        Notation: mx_k = E[x_k] and my_k = E[y_k], where m stands for "mean of"
        """
        
        xDim    = self.z.size                           # dimension of the state

        mx_kp1  = self.f(self.z, u)                               # predict next state
        A       = self.numerical_jac(self.f, self.z, u, modeGPS)  # linearize process model about current state

        P_kp1   = dot(dot(A,self.P),A.T) + self.Q                 # proprogate variance

        my_kp1  = self.h(mx_kp1, u, modeGPS)                      # predict future output
        H       = self.numerical_jac(self.h, mx_kp1, u, modeGPS)  # linearize measurement model about predicted next state
        
        P12     = dot(P_kp1, H.T)                                 # cross covariance

        if modeGPS == True:
            K       = dot(P12, inv( dot(H,P12) + self.R))       # Kalman filter gain
        else:
            K       = dot(P12, inv( dot(H,P12) + self.R[2:,2:]))       # Kalman filter gain
            
        self.z  = mx_kp1 + dot(K,(y - my_kp1))

        if modeGPS == True:
            self.P  = dot(dot(K,self.R),K.T) + dot( dot( (eye(xDim) - dot(K,H)) , P_kp1)  ,  (eye(xDim) - dot(K,H)).T )
        else:
            self.P  = dot(dot(K,self.R[2:,2:]),K.T) + dot( dot( (eye(xDim) - dot(K,H)) , P_kp1)  ,  (eye(xDim) - dot(K,H)).T )

        (self.x_est, self.y_est, self.vx_est, self.vy_est, self.ax_est, self.ay_est, self.yaw_est, self.psiDot_est) = self.z


    def ukf(self, y, u):
        """
        UKF   Unscented Kalman Filter for nonlinear dynamic systems
        ekf(f,mx,P,h,z,Q,R) returns state estimate, x and state covariance, P 
        for nonlinear dynamic system:
                  x[k] = f(x[k-1],u[k-1]) + v[k-1]
                  y[k] = h(x[k]) + w[k]
        where v ~ N(0,Q) meaning v is gaussian noise with covariance Q
              w ~ N(0,R) meaning w is gaussian noise with covariance R
        Inputs:    f: function handle for f(x)
                   h: function handle for h(x)
                   y: current measurement
                   Q: process noise covariance 
                   R: measurement noise covariance
        Output:    mx_k: "a posteriori" state estimate
                   P_k: "a posteriori" state covariance
                   
        Notation: mx_k = E[x_k] and my_k = E[y_k], where m stands for "mean of"
        """

        # sigma-points: generate a list, "sm_km1"
        xDim        = self.z.size
        sqrtnP      = cholesky(xDim*self.P)
        sm_km1      = list(add(self.z,sqrtnP))
        sm_km1.extend(list(add(self.z,-sqrtnP)))

        # prior update
        sx_k = [self.f(s, u) for s in sm_km1]
        mx_k = 1.0/len(sx_k)*sum(sx_k)
        P_m  = self.Q + 1.0/len(sx_k)*sum([np.outer((sx-mx_k),(sx-mx_k)) for sx in sx_k])

        # posterior update
        sy_k = [self.h(s, u) for s in sx_k]
        my_k = 1.0/len(sy_k)*sum(sy_k)
        P_zz  = self.R + 1.0/len(sy_k)*sum([np.outer((sy-my_k),(sy-my_k)) for sy in sy_k])

        # cross covariance
        P_xz = 1.0/len(sy_k)*sum([np.outer((sx_k[i]-mx_k),(sy_k[i]-my_k)) for i in range(len(sy_k))])

        # Kalman filter
        K = dot(P_xz,inv(P_zz))
        self.z = mx_k + dot(K, y-my_k)
        self.P = P_m - dot(K, dot(P_zz, K.T))
        
        (self.x_est, self.y_est, self.vx_est, self.vy_est, self.ax_est, self.ay_est, self.yaw_est, self.psiDot_est) = self.z

    def numerical_jac(self,func,x,u, modeGPS):
        """
        Function to compute the numerical jacobian of a vector valued function 
        using final differences
        """
        # numerical gradient and diagonal hessian
        y = func(x,u, modeGPS)
        
        jac = zeros( (y.size,x.size) )
        eps = 1e-5
        xp = np.copy(x)
        
        for i in range(x.size):
            xp[i] = x[i] + eps/2.0
            yhi = func(xp, u, modeGPS)
            xp[i] = x[i] - eps/2.0
            ylo = func(xp, u, modeGPS)
            xp[i] = x[i]
            jac[:,i] = (yhi - ylo) / eps
        return jac

    def f(self, z, u, modeGPS=True):
        """ This Sensor model contains a pure Sensor-Model and a Kinematic model. They're independent from each other."""
        dt = self.dt

        if self.dynamic_model:
            x, y, v_x, v_y, a_x, a_y, psi, psi_dot = z
            c_f = self.front_corner_stiffness
            c_r = self.rear_corner_stiffness
            l_f = self.l_f
            l_r = self.l_r
            m = self.mass
            I_z = self.I_z
            x_next = x + dt * (cos(psi) * v_x - sin(psi) * v_y)
            y_next = y + dt * (sin(psi) * v_x + cos(psi) * v_y)
            vx_next = v_x + dt * (a_x + psi_dot * v_y)
            vy_dot = ((- c_f - c_r) / (m * v_x)) * v_y + \
                     (- v_x - (l_f * c_f - l_r * c_r) / (m * v_x)) * psi_dot + \
                     (c_f / m) * u[1]
            vy_next = v_y + dt * vy_dot
            ax_next = a_x 
            ay_next = a_y
            psi_next = psi + dt * psi_dot
            psidot_dot = ((- l_f * c_f + l_r * c_r) / (I_z * v_x)) * v_y + \
                         ((- l_f**2 * c_f - l_r**2 * c_r) / (I_z * v_x)) * psi_dot + \
                         (l_f * c_f / I_z) * u[1]
            psidot_next = psi_dot + dt * psidot_dot
            return np.array([x_next, y_next, vx_next, vy_next, ax_next, ay_next, psi_next, psidot_next])
        else:
            zNext = [0]*8
            zNext[0] = z[0] + dt*(cos(z[6])*z[2] - sin(z[6])*z[3])  # x
            zNext[1] = z[1] + dt*(sin(z[6])*z[2] + cos(z[6])*z[3])  # y
            zNext[2] = z[2] + dt*(z[4]+z[7]*z[3])                   # v_x
            zNext[3] = z[3] + dt*(z[5]-z[7]*z[2])                   # v_y
            zNext[4] = z[4]                                         # a_x
            zNext[5] = z[5]                                         # a_y
            zNext[6] = z[6] + dt*(z[7])                             # psi
            zNext[7] = z[7]                                         # psidot
            return np.array(zNext)

    def h(self, x, u, modeGPS):
        """ This is the measurement model to the kinematic<->sensor model above """
        if self.dynamic_model:
            c_f = self.front_corner_stiffness
            c_r = self.rear_corner_stiffness
            l_f = self.l_f
            l_r = self.l_r
            m = self.mass
            x, y, v_x, v_y, a_x, a_y, psi, psi_dot = x
            x_meas = x
            y_meas = y
            vx_meas = v_x
            ax_meas = a_x
            ay_meas = ((- c_f - c_r) / (m * v_x)) * v_y + \
                      ((- l_f * c_f + l_r * c_r) / (m * v_x)) * psi_dot + \
                      (c_f / m) * u[1]
            psidot_meas = psi_dot
            return np.array([x_meas, y_meas, vx_meas, ax_meas, ay_meas, psidot_meas])
        elif modeGPS:
            y = [0]*7
            y[0] = x[0]   # x
            y[1] = x[1]   # y
            y[2] = x[2]   # vx
            y[3] = x[4]   # a_x
            y[4] = x[5]   # a_y
            y[5] = x[7]   # psiDot
            y[6] = x[3]   # vy
        else:
            y = [0]*5
            y[0] = x[2]   # vx
            y[1] = x[4]   # a_x
            y[2] = x[5]   # a_y
            y[3] = x[7]   # psiDot
            y[4] = x[3]   # vy
        return np.array(y)

    def saveHistory(self):
        self.time_his.append(self.curr_time)

        self.x_est_his.append(self.x_est)
        self.y_est_his.append(self.y_est)
        self.vx_est_his.append(self.vx_est)
        self.vy_est_his.append(self.vy_est)
        self.v_est_his.append(self.v_est)
        self.ax_est_his.append(self.ax_est)
        self.ay_est_his.append(self.ay_est)
        self.yaw_est_his.append(self.yaw_est)
        self.psiDot_est_his.append(self.psiDot_est)

# ========================================================================================================================================
# ======================================================= ESTIMATOR NO VY ================================================================
# ========================================================================================================================================
class EstimatorNoVy(object):
    """ Object collecting  estimated state data
    Attributes:
        Estimated states:
            1.x_est     2.y_est
            3.vx_est    4.vy_est        5.v_est
            6.ax_est    7.ay_est
            8.yaw_est   9.psiDot_est    10.psiDrift_est
        Estimated states history:
            1.x_est_his     2.y_est_his
            3.vx_est_his    4.vy_est_his        5.v_est_his
            6.ax_est_his    7.ay_est_his
            8.yaw_est_his   9.psiDot_est_his    10.psiDrift_est_his
        Time stamp
            1.t0 2.time_his 3.curr_time
    Methods:
        stateEstimate(imu,gps,enc,ecu):
            Estimate current state from sensor data
        ekf(y,u):
            Extended Kalman filter
        ukf(y,u):
            Unscented Kalman filter
        numerical_jac(func,x,u):
            Calculate jacobian numerically
        f(x,u):
            System prediction model
        h(x,u):
            System measurement model
    """

    def __init__(self,t0,loop_rate,a_delay,df_delay,Q,R,thReset):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """
        self.thReset = thReset

        dt          = 1.0 / loop_rate
        self.rate   = rospy.Rate(loop_rate)
        L_f         = rospy.get_param("L_a")       # distance from CoG to front axel
        L_r         = rospy.get_param("L_b")       # distance from CoG to rear axel
        self.vhMdl  = (L_f, L_r)
        self.Q      = Q
        self.R      = R
        self.P      = np.eye(np.size(Q,0)) # initializationtial covariance matrix
        self.z      = np.zeros(np.size(Q,0)) # initial state mean
        self.dt     = dt
        self.a_delay        = a_delay
        self.df_delay       = df_delay
        self.a_his          = [0.0]*int(a_delay/dt)
        self.df_his         = [0.0]*int(df_delay/dt)

        self.state_pub_pos  = rospy.Publisher('pos_info', pos_info, queue_size=1)
        self.t0             = t0

        self.x_est          = 0.0
        self.y_est          = 0.0
        self.vx_est         = 0.0
        self.vy_est         = 0.0
        self.v_est          = 0.0
        self.ax_est         = 0.0
        self.ay_est         = 0.0
        self.yaw_est        = 0.0
        self.psiDot_est     = 0.0
        self.psiDrift_est   = 0.0
        self.curr_time      = rospy.get_rostime().to_sec()

        self.x_est_his          = []
        self.y_est_his          = []
        self.vx_est_his         = []
        self.vy_est_his         = []
        self.v_est_his          = []
        self.ax_est_his         = []
        self.ay_est_his         = []
        self.yaw_est_his        = []
        self.psiDot_est_his     = []
        self.time_his           = []

        # SAVE THE measurement/input SEQUENCE USED BY KF
        self.x_his      = []
        self.y_his      = []
        self.v_meas_his = []
        self.ax_his     = []
        self.ay_his     = []
        self.psiDot_his = []
        self.inp_a_his  = []
        self.inp_df_his = []

        self.gps_time = []
        self.enc_time = []
        self.imu_time = []

        self.oldGPS_x = 0.0
        self.oldGPS_y = 0.0

    # ecu command update
    def estimateState(self,imu,gps,enc,ecu,KF):
        """Do extended Kalman filter to estimate states"""
        self.curr_time = rospy.get_rostime().to_sec()

        self.a_his.append(ecu.a)
        self.df_his.append(ecu.df)
        u = [self.a_his.pop(0), self.df_his.pop(0)]
        # u = [ecu.a, self.df_his.pop(0)]
        
        bta = 0.5 * u[1]
        dist   = np.sqrt(( self.x_est - gps.x )**2 + ( self.y_est - gps.y )**2)

        # if ( dist >= 1 ) or ( (gps.x == self.oldGPS_x) and (gps.x == self.oldGPS_y) ):
        # if ( (gps.x == self.oldGPS_x) and (gps.x == self.oldGPS_y) ):
        if 0 == 1:
            modeGPS = False
            y = np.array([enc.v_meas, imu.ax, imu.ay, imu.psiDot])
        else:
            modeGPS = True
            y = np.array([gps.x, gps.y, enc.v_meas, imu.ax, imu.ay, imu.psiDot])


        self.oldGPS_x = gps.x
        self.oldGPS_y = gps.y

        if np.abs(imu.psiDot) < self.thReset:
            self.z[3] = 0

        KF(y,u, modeGPS)


        # SAVE THE measurement/input SEQUENCE USED BY KF
        self.x_his.append(gps.x)
        self.y_his.append(gps.y)
        self.v_meas_his.append(enc.v_meas)
        self.ax_his.append(imu.ax)
        self.ay_his.append(imu.ay)
        self.psiDot_his.append(imu.psiDot)
        self.inp_a_his.append(u[0])
        self.inp_df_his.append(u[1])

        self.gps_time.append(gps.curr_time)
        self.imu_time.append(imu.curr_time)
        self.enc_time.append(enc.curr_time)
        # SAVE output KF given the above measurements
        self.saveHistory()

    def ekf(self, y, u, modeGPS):
        """
        EKF   Extended Kalman Filter for nonlinear dynamic systems
        ekf(f,mx,P,h,z,Q,R) returns state estimate, x and state covariance, P 
        for nonlinear dynamic system:
                  x_k+1 = f(x_k) + w_k
                  y_k   = h(x_k) + v_k
        where w ~ N(0,Q) meaning w is gaussian noise with covariance Q
              v ~ N(0,R) meaning v is gaussian noise with covariance R
        Inputs:    f: function handle for f(x)
                   z_EKF: "a priori" state estimate
                   P: "a priori" estimated state covariance
                   h: fanction handle for h(x)
                   y: current measurement
                   Q: process noise covariance 
                   R: measurement noise covariance
                   args: additional arguments to f(x, *args)
        Output:    mx_kp1: "a posteriori" state estimate
                   P_kp1: "a posteriori" state covariance
                   
        Notation: mx_k = E[x_k] and my_k = E[y_k], where m stands for "mean of"
        """
        
        xDim    = self.z.size                           # dimension of the state

        mx_kp1  = self.f(self.z, u)                               # predict next state
        A       = self.numerical_jac(self.f, self.z, u, modeGPS)  # linearize process model about current state

        P_kp1   = dot(dot(A,self.P),A.T) + self.Q                 # proprogate variance

        my_kp1  = self.h(mx_kp1, u, modeGPS)                      # predict future output
        H       = self.numerical_jac(self.h, mx_kp1, u, modeGPS)  # linearize measurement model about predicted next state
        
        P12     = dot(P_kp1, H.T)                                 # cross covariance

        if modeGPS == True:
            K       = dot(P12, inv( dot(H,P12) + self.R))       # Kalman filter gain
        else:
            K       = dot(P12, inv( dot(H,P12) + self.R[2:,2:]))       # Kalman filter gain
            
        self.z  = mx_kp1 + dot(K,(y - my_kp1))

        if modeGPS == True:
            self.P  = dot(dot(K,self.R),K.T) + dot( dot( (eye(xDim) - dot(K,H)) , P_kp1)  ,  (eye(xDim) - dot(K,H)).T )
        else:
            self.P  = dot(dot(K,self.R[2:,2:]),K.T) + dot( dot( (eye(xDim) - dot(K,H)) , P_kp1)  ,  (eye(xDim) - dot(K,H)).T )

        (self.x_est, self.y_est, self.vx_est, self.vy_est, self.ax_est, self.ay_est, self.yaw_est, self.psiDot_est) = self.z


    def ukf(self, y, u):
        """
        UKF   Unscented Kalman Filter for nonlinear dynamic systems
        ekf(f,mx,P,h,z,Q,R) returns state estimate, x and state covariance, P 
        for nonlinear dynamic system:
                  x[k] = f(x[k-1],u[k-1]) + v[k-1]
                  y[k] = h(x[k]) + w[k]
        where v ~ N(0,Q) meaning v is gaussian noise with covariance Q
              w ~ N(0,R) meaning w is gaussian noise with covariance R
        Inputs:    f: function handle for f(x)
                   h: function handle for h(x)
                   y: current measurement
                   Q: process noise covariance 
                   R: measurement noise covariance
        Output:    mx_k: "a posteriori" state estimate
                   P_k: "a posteriori" state covariance
                   
        Notation: mx_k = E[x_k] and my_k = E[y_k], where m stands for "mean of"
        """

        # sigma-points: generate a list, "sm_km1"
        xDim        = self.z.size
        sqrtnP      = cholesky(xDim*self.P)
        sm_km1      = list(add(self.z,sqrtnP))
        sm_km1.extend(list(add(self.z,-sqrtnP)))

        # prior update
        sx_k = [self.f(s, u) for s in sm_km1]
        mx_k = 1.0/len(sx_k)*sum(sx_k)
        P_m  = self.Q + 1.0/len(sx_k)*sum([np.outer((sx-mx_k),(sx-mx_k)) for sx in sx_k])

        # posterior update
        sy_k = [self.h(s, u) for s in sx_k]
        my_k = 1.0/len(sy_k)*sum(sy_k)
        P_zz  = self.R + 1.0/len(sy_k)*sum([np.outer((sy-my_k),(sy-my_k)) for sy in sy_k])

        # cross covariance
        P_xz = 1.0/len(sy_k)*sum([np.outer((sx_k[i]-mx_k),(sy_k[i]-my_k)) for i in range(len(sy_k))])

        # Kalman filter
        K = dot(P_xz,inv(P_zz))
        self.z = mx_k + dot(K, y-my_k)
        self.P = P_m - dot(K, dot(P_zz, K.T))
        
        (self.x_est, self.y_est, self.vx_est, self.vy_est, self.ax_est, self.ay_est, self.yaw_est, self.psiDot_est) = self.z

    def numerical_jac(self,func,x,u, modeGPS):
        """
        Function to compute the numerical jacobian of a vector valued function 
        using final differences
        """
        # numerical gradient and diagonal hessian
        y = func(x,u, modeGPS)
        
        jac = zeros( (y.size,x.size) )
        eps = 1e-5
        xp = np.copy(x)
        
        for i in range(x.size):
            xp[i] = x[i] + eps/2.0
            yhi = func(xp, u, modeGPS)
            xp[i] = x[i] - eps/2.0
            ylo = func(xp, u, modeGPS)
            xp[i] = x[i]
            jac[:,i] = (yhi - ylo) / eps
        return jac

    def f(self, z, u, modeGPS=True):
        """ This Sensor model contains a pure Sensor-Model and a Kinematic model. They're independent from each other."""
        dt = self.dt
        zNext = [0]*8
        zNext[0] = z[0] + dt*(cos(z[6])*z[2] - sin(z[6])*z[3])  # x
        zNext[1] = z[1] + dt*(sin(z[6])*z[2] + cos(z[6])*z[3])  # y
        zNext[2] = z[2] + dt*(z[4]+z[7]*z[3])                   # v_x
        zNext[3] = z[3] + dt*(z[5]-z[7]*z[2])                   # v_y
        zNext[4] = z[4]                                         # a_x
        zNext[5] = z[5]                                         # a_y
        zNext[6] = z[6] + dt*(z[7])                             # psi
        zNext[7] = z[7]                                         # psidot
        return np.array(zNext)

    def h(self, x, u, modeGPS):
        """ This is the measurement model to the kinematic<->sensor model above """
        if modeGPS:
            y = [0]*6
            y[0] = x[0]   # x
            y[1] = x[1]   # y
            y[2] = x[2]   # vx
            y[3] = x[4]   # a_x
            y[4] = x[5]   # a_y
            y[5] = x[7]   # psiDot
            # y[6] = x[3]   # vy
        else:
   
            y[0] = x[2]   # vx
            y[1] = x[4]   # a_x
            y[2] = x[5]   # a_y
            y[3] = x[7]   # psiDot
            # y[4] = x[3]   # vy
        return np.array(y)

    def saveHistory(self):
        self.time_his.append(self.curr_time)

        self.x_est_his.append(self.x_est)
        self.y_est_his.append(self.y_est)
        self.vx_est_his.append(self.vx_est)
        self.vy_est_his.append(self.vy_est)
        self.v_est_his.append(self.v_est)
        self.ax_est_his.append(self.ax_est)
        self.ay_est_his.append(self.ay_est)
        self.yaw_est_his.append(self.yaw_est)
        self.psiDot_est_his.append(self.psiDot_est)


# ========================================================================================================================================
# ======================================================= SENSOR CLASSES =================================================================
# ========================================================================================================================================

class ImuClass(object):
    """ Object collecting GPS measurement data
    Attributes:
        Measurement:
            1.yaw 2.psiDot 3.ax 4.ay 5.roll 6.pitch
        Measurement history:
            1.yaw_his 2.psiDot_his 3.ax_his 4.ay_his 5.roll_his 6.pitch_his
        Time stamp
            1.t0 2.time_his
    """
    def __init__(self,t0):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """

        rospy.Subscriber('imu/data', Imu, self.imu_callback, queue_size=1)

        # Imu measurement
        self.yaw     = 0.0
        self.psiDot  = 0.0
        self.ax      = 0.0
        self.ay      = 0.0
        self.roll    = 0.0
        self.pitch   = 0.0
        
        # Imu measurement history
        self.yaw_his     = []
        self.psiDot_his  = []
        self.ax_his      = []
        self.ay_his      = []
        self.roll_his    = []
        self.pitch_his   = []
        
        # time stamp
        self.t0          = t0
        self.time_his    = []

        # Time for yawDot integration
        self.curr_time = rospy.get_rostime().to_sec()
        self.prev_time = self.curr_time

    def imu_callback(self,data):
        """Unpack message from sensor, IMU"""
        
        self.curr_time = rospy.get_rostime().to_sec()

        if self.prev_time > 0:
            self.yaw += self.psiDot * (self.curr_time-self.prev_time)
   
        ori = data.orientation
        quaternion = (ori.x, ori.y, ori.z, ori.w)
        (roll_raw, pitch_raw, dummy) = transformations.euler_from_quaternion(quaternion)
        self.roll   = roll_raw
        self.pitch  = pitch_raw

        w_z = data.angular_velocity.z
        a_x = data.linear_acceleration.x
        a_y = data.linear_acceleration.y
        a_z = data.linear_acceleration.z

        self.psiDot = w_z
        # Transformation from imu frame to vehicle frame (negative roll/pitch and reversed matrix multiplication to go back)
        self.ax = cos(-pitch_raw)*a_x + sin(-pitch_raw)*sin(-roll_raw)*a_y - sin(-pitch_raw)*cos(-roll_raw)*a_z
        self.ay = cos(-roll_raw)*a_y + sin(-roll_raw)*a_z

        self.prev_time = self.curr_time

        self.saveHistory()

    def saveHistory(self):
        """ Save measurement data into history array"""

        self.time_his.append(self.curr_time)
        
        self.yaw_his.append(self.yaw)
        self.psiDot_his.append(self.psiDot)
        self.ax_his.append(self.ax)
        self.ay_his.append(self.ay)
        self.roll_his.append(self.roll)
        self.pitch_his.append(self.pitch)



class GpsClass(object):
    """ Object collecting GPS measurement data
    Attributes:
        Measurement:
            1.x 2.y
        Measurement history:
            1.x_his 2.y_his
        Time stamp
            1.t0 2.time_his 3.curr_time
    """
    def __init__(self,t0):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """
        rospy.Subscriber('hedge_pos', hedge_pos, self.gps_callback, queue_size=1)
        # rospy.Subscriber('hedge_imu_fusion', hedge_imu_fusion, self.gps_callback, queue_size=1)

        # GPS measurement
        self.x      = 0.0
        self.y      = 0.0
        
        # GPS measurement history
        self.x_his  = np.array([])
        self.y_his  = np.array([])
        
        # time stamp
        self.t0         = t0
        self.time_his   = np.array([])
        self.curr_time  = rospy.get_rostime().to_sec() 

    def gps_callback(self,data):
        """Unpack message from sensor, GPS"""
        if 2 == data.flags:
            self.curr_time = rospy.get_rostime().to_sec()

            self.x = data.x_m
            self.y = data.y_m

            # 1) x(t) ~ c0x + c1x * t + c2x * t^2
            # 2) y(t) ~ c0y + c1y * t + c2y * t^2
            # c_X = [c0x c1x c2x] and c_Y = [c0y c1y c2y] 
            # n_intplt = 20
            # if size(self.x_his,0) > n_intplt: # do interpolation when there is enough points
            #     x_intplt = self.x_his[-n_intplt:]
            #     y_intplt = self.y_his[-n_intplt:]
            #     t_intplt = self.time_his[-n_intplt:]
            #     t_matrix = vstack([t_intplt**2, t_intplt, ones(sz)]).T
            #     self.c_X = linalg.lstsq(t_matrix, x_intplt)[0]
            #     self.c_Y = linalg.lstsq(t_matrix, y_intplt)[0]
            #     self.x = polyval(self.c_X, self.curr_time)
            #     self.y = polyval(self.c_Y, self.curr_time)

            self.saveHistory()

    def saveHistory(self):
        self.time_his = np.append(self.time_his,self.curr_time)

        self.x_his = np.append(self.x_his,self.x)
        self.y_his = np.append(self.y_his,self.y)


class EncClass(object):
    """ Object collecting ENC measurement data
    Attributes:
        Measurement:
            1.v_fl 2.v_fr 3. v_rl 4. v_rr
        Measurement history:
            1.v_fl_his 2.v_fr_his 3. v_rl_his 4. v_rr_his
        Time stamp
            1.t0 2.time_his 3.curr_time
    """
    def __init__(self,t0):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """
        rospy.Subscriber('vel_est', Vel_est, self.enc_callback, queue_size=1)

        node_name = rospy.get_name()
        if node_name[-1] == "2":
            self.use_both_encoders = False
        else:
            self.use_both_encoders = True

        # ENC measurement
        self.v_fl      = 0.0
        self.v_fr      = 0.0
        self.v_rl      = 0.0
        self.v_rr      = 0.0
        self.v_meas    = 0.0
        
        # ENC measurement history
        self.v_fl_his    = []
        self.v_fr_his    = []
        self.v_rl_his    = []
        self.v_rr_his    = []
        self.v_meas_his  = []
        
        # time stamp
        self.v_count    = 0
        self.v_prev     = 0.0
        self.t0         = t0
        self.time_his   = []
        self.curr_time  = rospy.get_rostime().to_sec()

    def enc_callback(self,data):
        """Unpack message from sensor, ENC"""
        self.curr_time = rospy.get_rostime().to_sec()

        self.v_fl = data.vel_fl
        self.v_fr = data.vel_fr
        self.v_rl = data.vel_bl
        self.v_rr = data.vel_br

        if self.use_both_encoders:
            v_est = (self.v_rl + self.v_rr) / 2.0
        else:
            v_est = self.v_rr

        if v_est != self.v_prev:
            self.v_meas = v_est
            self.v_prev = v_est
            self.v_count = 0
        else:
            self.v_count += 1
            if self.v_count > 10 and self.v_meas < 0.5:     # if 10 times in a row the same measurement
                self.v_meas = 0       # set velocity measurement to zero

        self.saveHistory()

    def saveHistory(self):
        self.time_his.append(self.curr_time)
        
        self.v_fl_his.append(self.v_fl)
        self.v_fr_his.append(self.v_fr)
        self.v_rl_his.append(self.v_rl)
        self.v_rr_his.append(self.v_rr)

        self.v_meas_his.append(self.v_meas)

class EcuClass(object):
    """ Object collecting CMD command data
    Attributes:
        Input command:
            1.a 2.df
        Input command history:
            1.a_his 2.df_his
        Time stamp
            1.t0 2.time_his 3.curr_time
    """
    def __init__(self,t0):
        """ Initialization
        Arguments:
            t0: starting measurement time
        """
        rospy.Subscriber('ecu', ECU, self.ecu_callback, queue_size=1)

        # ECU measurement
        self.a  = 0.0
        self.df = 0.0
        
        # ECU measurement history
        self.a_his  = []
        self.df_his = []
        
        # time stamp
        self.t0         = t0
        self.time_his   = []
        self.curr_time  = rospy.get_rostime().to_sec()

    def ecu_callback(self,data):
        """Unpack message from sensor, ECU"""
        self.curr_time = rospy.get_rostime().to_sec()

        self.a  = data.motor
        self.df = data.servo

        self.saveHistory()

    def saveHistory(self):
        self.time_his.append(self.curr_time)
        
        self.a_his.append(self.a)
        self.df_his.append(self.df)


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass