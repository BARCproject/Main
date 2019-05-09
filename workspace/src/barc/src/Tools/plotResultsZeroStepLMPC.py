import sys
sys.path.append(sys.path[0]+'/../ControllersObject')
sys.path.append(sys.path[0]+'/../Utilities')
from dataStructures import LMPCprediction, EstimatorData, ClosedLoopDataObj, LMPCprediction

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from LMPC import ControllerLMPC
import sys
import pickle
import pdb
from trackInitialization import Map
from dataStructures import LMPCprediction, EstimatorData, ClosedLoopDataObj
import os
from numpy import linalg as la

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# matplotlib.rcParams['pdf.fonttype']=42
# matplotlib.rcParams['ps.fonttype']=42

def main():
    homedir = os.path.expanduser("~")

    file_data = open(homedir+'/barc_data/ClosedLoopDataZeroStep.obj', 'rb')    
    ClosedLoopData = pickle.load(file_data)
    LMPController = pickle.load(file_data)
    LMPCOpenLoopData = pickle.load(file_data)    
    file_data.close()
    map = LMPController.map


    pdb.set_trace()
    print "Track length is: ", map.TrackLength

    # # Plot Lap Time
    # plt.figure()
    # plt.plot([i*LMPController.dt for i in LMPController.LapCounter[1:LMPController.it]], '-o', label="Lap Time")
    # plt.legend()
    # plt.show()

    # # Plot First Path Following Lap and Learning laps
    # LapToPlotLearningProcess = [2,3,5,10,15]
    # plotClosedLoopLMPC(LMPController, map, LapToPlotLearningProcess)

    # # Plot Best Laps
    # LapToPlot      = range(0, LMPController.it)
    # BestNunberLaps = 4
    # SortedTimes    = np.sort(LMPController.LapCounter[1:LMPController.it])
    # LapToPlot      = np.argsort(LMPController.LapCounter[1:LMPController.it])[0:BestNunberLaps]
    # LapToPlot = range(24,28)
    # print SortedTimes
    # print "Lap Plotted: ", LapToPlot, " Lap Time: ", LMPController.LapCounter[LapToPlot]
    # plotClosedLoopColorLMPC(LMPController, map, LapToPlot)
    
    # plotClosedLoopLMPC(LMPController, map, LapToPlot)
    # # Plot Acceleration
    # plotAccelerations(LMPController, LapToPlot, map)
    
    # plt.show()

    # # Plot One Step Prediction Error
    # plotOneStepPreditionError(LMPController, LMPCOpenLoopData, LapToPlotLearningProcess)
    # plt.show()



    # Computational Time
    lapLMPC     = []
    lapTimeLMPC = []
    lapZeroStep = []
    lapTimeZS   = []

    LMPC = 1
    lapCounterLoop = 0
    for i in  range(2, LMPController.it):
        if (LMPController.LapCounter[i] > 0) and (lapCounterLoop < 60):
            lapCounterLoop = lapCounterLoop + 1
            if LMPC == 1:
                lapLMPC.append(lapCounterLoop)
                lapTimeLMPC.append(LMPController.LapCounter[i]*0.1)
            else:
                lapZeroStep.append(lapCounterLoop)
                lapTimeZS.append(LMPController.LapCounter[i]*0.1)
        else:
            LMPC = 0

    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')

    # LapToPlot = range(0,50)
    # plotComputationalTime(LMPController, LapToPlot, map, 10)
    # plt.show()
    
    plt.figure()

    plt.plot(lapLMPC, lapTimeLMPC, 'bo', label="LMPC")
    plt.plot(lapZeroStep, lapTimeZS, 'rs', label="Data-Based Policy")
    plt.legend(prop={'size': 16})
    plt.ylim(0,20)

    plt.xlabel("Lap Number", fontsize = 16)
    plt.ylabel("Lap Time [s]", fontsize = 16)

    print("LMPC LapTime: ", lapTimeLMPC)
    print("ZeroStep LapTime: ", lapTimeZS)
    plt.show()

    # # For LMPC_1 Oval New Car # Used in ACC paper
    # LapToPlot = [26, 24, 29] 
    # LapToPlot.append(33); LapToPlot.append(39)

    # For LMPC_2 Oval New Car
    # LapToPlot = [24,25, 26] 
    # LapToPlot.append(43); LapToPlot.append(44)

    # # For LMPC_1 3110_big
    # LapToPlot = [16,17, 18] 
    # LapToPlot.append(36); LapToPlot.append(37)

    # # For Simulations
    # LapToPlot = [27,28,29] 
    # LapToPlot.append(36); LapToPlot.append(37)    

    # # Oval 6_LMPC_60Laps
    # LapToPlot = [26,27]
    # LapToPlot.append(32); LapToPlot.append(33)    

    # # 3110_big 6_LMPC_AfterVideo10LapsZeroStep
    # LapToPlot = [27, 29]
    # LapToPlot.append(34); LapToPlot.append(32) 

    # # 3110_big 2_LMPC_FromCoderLinear
    # LapToPlot = [26, 28]
    # LapToPlot.append(36); LapToPlot.append(39) 
    
    # L_shape 6_LMPC_40LapsNiceVideo
    # LapToPlot = [23, 27]
    # LapToPlot.append(35); LapToPlot.append(32) 

    # L_shape 6_LMPC_42LapsNiceVideo # Used in ACC paper
    LapToPlot = [21, 26, 27]
    LapToPlot.append(35); LapToPlot.append(33) 

 
    print LapToPlot

    groupFlag = 2
    print "Lap Time: ", LMPController.LapCounter[LapToPlot]
    plotClosedLoopLMPC(LMPController, map, LapToPlot, groupFlag)

    plotComputationalTime(LMPController, LapToPlot, map, groupFlag)
    plt.show()

    plotClosedLoopColorLMPC(LMPController, map, [35])
    plt.show()

    print "Do you wanna create xy gif? [Lap #/n]"
    inputKeyBoard = raw_input()
    if inputKeyBoard != "n":
        saveGif_xyResults(map, LMPCOpenLoopData, LMPController, int(inputKeyBoard))
    
    # pdb.set_trace()
    # animation_states(map, LMPCOpenLoopData, LMPController, 10)

    # plt.show()
    
def plotAccelerations(LMPController, LapToPlot, map):
    n = LMPController.n
    x = np.zeros((10000, 1, LMPController.it+2))
    s = np.zeros((10000, 1, LMPController.it+2))
    y = np.zeros((10000, 1, LMPController.it+2))
    ax = np.zeros((10000, 1, LMPController.it+2))
    ay = np.zeros((10000, 1, LMPController.it+2))
    psiDot = np.zeros((10000, 1, LMPController.it+2))
    roll = np.zeros((10000, 1, LMPController.it+2))
    pitch = np.zeros((10000, 1, LMPController.it+2))
    LapCounter = np.zeros(LMPController.it+2)

    homedir = os.path.expanduser("~")
    pathSave = os.path.join(homedir,"barc_data/estimator_output.npz")
    npz_output = np.load(pathSave)
    x_est_his           = npz_output["x_est_his"]
    y_est_his           = npz_output["y_est_his"]
    vx_est_his          = npz_output["vx_est_his"] 
    vy_est_his          = npz_output["vy_est_his"] 
    ax_est_his          = npz_output["ax_est_his"] 
    ay_est_his          = npz_output["ay_est_his"] 
    psiDot_est_his      = npz_output["psiDot_est_his"]  
    yaw_est_his         = npz_output["yaw_est_his"]  
    gps_time            = npz_output["gps_time"]
    imu_time            = npz_output["imu_time"]
    enc_time            = npz_output["enc_time"]
    inp_x_his           = npz_output["inp_x_his"]
    inp_y_his           = npz_output["inp_y_his"]
    inp_v_meas_his      = npz_output["inp_v_meas_his"]
    inp_ax_his          = npz_output["inp_ax_his"]
    inp_ay_his          = npz_output["inp_ay_his"]
    inp_psiDot_his      = npz_output["inp_psiDot_his"]
    inp_a_his           = npz_output["inp_a_his"]
    inp_df_his          = npz_output["inp_df_his"]
    roll_his            = npz_output["roll_his"]
    pitch_his           = npz_output["pitch_his"]
    wx_his              = npz_output["wx_his"]
    wy_his              = npz_output["wy_his"]
    wz_his              = npz_output["wz_his"]
    v_rl_his            = npz_output["v_rl_his"]
    v_rr_his            = npz_output["v_rr_his"]
    v_fl_his            = npz_output["v_fl_his"]
    v_fr_his            = npz_output["v_fr_his"]
    yaw_his             = npz_output["psi_raw_his"]

    halfTrack = 0
    iteration = 0
    TimeCounter = 0
    for i in range(0, len(x_est_his)):
        s_i, ey_i, epsi_i, _ = map.getLocalPosition(x_est_his[i], y_est_his[i], yaw_est_his[i])
        
        if s_i > map.TrackLength/4 and s_i < map.TrackLength/4*3:
            halfTrack = 1
        
        if s_i < map.TrackLength/4 and halfTrack == 1:
            print "Finishced unpacking iteration: ", iteration
            halfTrack = 0
            iteration += 1
            LapCounter[iteration-1] = TimeCounter - 1
            LapCounter[iteration] = 0
            TimeCounter = 0

        s[TimeCounter, 0, iteration]      = s_i
        ax[TimeCounter, 0, iteration]     = inp_ax_his[i]
        ay[TimeCounter, 0, iteration]     = inp_ay_his[i]
        psiDot[TimeCounter, 0, iteration] = inp_psiDot_his[i]
        roll[TimeCounter, 0, iteration]   = roll_his[i]
        pitch[TimeCounter, 0, iteration]  = pitch_his[i]

        TimeCounter += 1


    plotColors = ['b','g','r','c','y','k','m']

    plt.figure()
    plt.subplot(511)
    counter = 0
    for i in LapToPlot:
        plt.plot(s[0:LapCounter[i], 0, i], ax[0:LapCounter[i], 0, i], '-o', label=i, color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=len(LapToPlot))

    plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('ax [m/s^2]')
    plt.subplot(512)
    counter = 0
    for i in LapToPlot:
        plt.plot(s[0:LapCounter[i], 0, i], ay[0:LapCounter[i], 0, i], '-o', color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('ay [m/s^2]')
    plt.subplot(513)
    counter = 0
    for i in LapToPlot:
        plt.plot(s[0:LapCounter[i], 0, i], psiDot[0:LapCounter[i], 0, i], '-o', color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('psiDot [rad/s]')
    
    plt.subplot(514)
    counter = 0
    for i in LapToPlot:
        plt.plot(s[0:LapCounter[i], 0, i], pitch[0:LapCounter[i], 0, i], '-o', color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('psiDot [rad/s]')

    plt.subplot(515)
    counter = 0
    for i in LapToPlot:
        plt.plot(s[0:LapCounter[i], 0, i], roll[0:LapCounter[i], 0, i], '-o', color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('psiDot [rad/s]')
    
    

def plotComputationalTime(LMPController, LapToPlot, map, groupFlag):
    SS_glob = LMPController.SS_glob
    LapCounter  = LMPController.LapCounter
    SS      = LMPController.SS
    uSS     = LMPController.uSS
    qpTime  = LMPController.qpTime
    sysIDTime  = LMPController.sysIDTime
    contrTime  = LMPController.contrTime

    if groupFlag < 10:
        if groupFlag == 0:
            plotPoint = ['-o','-o','-o','-s','-s','k','m']
            plotColors = ['b','g','r','c','y','k','m']
            Label = LapToPlot
        elif groupFlag == 1:
            plotPoint = ['-o','-o','-o','-s','-s','k','m']
            plotColors = ['b','b','r','r','k','m']
            Label = ["LMPC", "LMPC", "Data-Based Policy", "Data-Based Policy"]
        elif groupFlag == 2:
            plotPoint = ['-o','-o','-o','-s','-s','k','m']
            plotColors = ['b','b','b','r','r','k','m']
            Label = ["LMPC", "LMPC", "LMPC", "Data-Based Policy", "Data-Based Policy"]  


        plt.figure()
        plt.subplot(311)
        counter = 0
        for i in LapToPlot:
            if counter != 0 and (Label[counter-1] == Label[counter]):
                plt.plot(SS[0:LapCounter[i], 4, i], qpTime[0:LapCounter[i], i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
            else:
                plt.plot(SS[0:LapCounter[i], 4, i], qpTime[0:LapCounter[i], i], plotPoint[counter], label=Label[counter], color=plotColors[counter%len(plotColors)])

            counter += 1
        plt.legend(bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=len(LapToPlot), prop={'size': 16})

        plt.axvline(map.TrackLength, linewidth=4, color='g')
        plt.ylabel('QP solver time [s]')
        plt.subplot(312)
        counter = 0
        for i in LapToPlot:
            plt.plot(SS[0:LapCounter[i], 4, i], sysIDTime[0:LapCounter[i], i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
            counter += 1
        plt.axvline(map.TrackLength, linewidth=4, color='g')
        plt.ylabel('Sys ID time [s]')
        plt.subplot(313)
        counter = 0
        for i in LapToPlot:
            plt.plot(SS[0:LapCounter[i], 4, i], qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i], '-o', color=plotColors[counter%len(plotColors)])
            plt.plot(SS[0:LapCounter[i], 4, i], contrTime[0:LapCounter[i], i], '-*', color=plotColors[counter%len(plotColors)])
            counter += 1
        
        plt.axvline(map.TrackLength, linewidth=4, color='g')
        plt.ylabel('Total [s]')

        plt.figure()
        counter = 0
        for i in LapToPlot:
            vecTime = qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i]
            print("Lap: ",i," Min: ", min(vecTime), " Max: ",max(vecTime), " Avg: ", np.mean(vecTime), " Std: ", np.std(vecTime))
            if counter != 0 and (Label[counter-1] == Label[counter]):
                plt.semilogy(SS[0:LapCounter[i], 4, i], qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
            else:
                plt.semilogy(SS[0:LapCounter[i], 4, i], qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i], plotPoint[counter], label=Label[counter], color=plotColors[counter%len(plotColors)])

            counter += 1

        plt.legend(prop={'size': 16})
        plt.ylabel('Computational Time [s]', fontsize = 16)
        plt.xlabel('Curvilinear Abscissa [m]', fontsize = 16)

        compTime = np.empty((0))
        for i in LapToPlot:
            compTime =  np.append(compTime, qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i], axis=0)


        plt.figure()
        plt.plot(0.1*np.arange(0, np.shape(compTime)[0]), compTime,'-o')
        plt.ylabel('Computational Time [s]', fontsize = 16)
        plt.xlabel('Time [s]', fontsize = 16)

    avgLapTime = []
    for i in range(0, LMPController.it):
        # pdb.set_trace()
        avg = np.mean(qpTime[0:LapCounter[i], i] + sysIDTime[0:LapCounter[i], i])
        # print "Iteration: ", i, " Horizon: ", LMPController.N
        avgLapTime.append(avg)

    plt.figure()
    plt.plot(avgLapTime, "-o", label='Avarage Computational Time [s]')
    plt.legend()
    plt.xlabel("Lap Number")
    plt.show()

def plotOneStepPreditionError(LMPController, LMPCOpenLoopData, LapToPlot):
    LapCounter  = LMPController.LapCounter
    SS      = LMPController.SS
    uSS     = LMPController.uSS
    TotNumberIt = LMPController.it
    oneStepPredictionError = LMPCOpenLoopData.oneStepPredictionError

    plotColors = ['b','g','r','c','y','k','m']
    
    plt.figure(10)
    plt.subplot(611)
    plt.title("One Step Prediction Error")
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[0, 1:LapCounter[i], i], '-o', color=plotColors[counter], label=i)
        counter += 1
        plt.legend()
    plt.ylabel('vx [m/s]')
    plt.subplot(612)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[1, 1:LapCounter[i], i], '-o', color=plotColors[counter])
        counter += 1
    plt.ylabel('vy [m/s]')
    plt.subplot(613)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[2, 1:LapCounter[i], i], '-o', color=plotColors[counter])
        counter += 1
    plt.ylabel('wz [rad/s]')
    plt.subplot(614)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[3, 1:LapCounter[i], i], '-o', color=plotColors[counter])
        counter += 1
    plt.ylabel('epsi [rad]')
    plt.subplot(615)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[4, 1:LapCounter[i], i], '-o', color=plotColors[counter])
        counter += 1
    plt.ylabel('s [m]')
    plt.subplot(616)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[1:LapCounter[i], 4, i], oneStepPredictionError[5, 1:LapCounter[i], i], '-o', color=plotColors[counter])
        counter += 1
    plt.ylabel('ey [m]')
    plt.xlabel('s [m]')



def plotTrajectory(map, ClosedLoop):
    x = ClosedLoop.x
    x_glob = ClosedLoop.x_glob
    u = ClosedLoop.u
    
    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((int(Points), 2))
    Points2 = np.zeros((int(Points), 2))
    Points0 = np.zeros((int(Points), 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    plt.figure()
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')
    plt.plot(x_glob[:, 4], x_glob[:, 5], '-r')

    plt.figure()
    plt.subplot(711)
    plt.plot(x[:, 4], x[:, 0], '-o')
    plt.ylabel('vx')
    plt.subplot(712)
    plt.plot(x[:, 4], x[:, 1], '-o')
    plt.ylabel('vy')
    plt.subplot(713)
    plt.plot(x[:, 4], x[:, 2], '-o')
    plt.ylabel('wz')
    plt.subplot(714)
    plt.plot(x[:, 4], x[:, 3], '-o')
    plt.ylabel('epsi')
    plt.subplot(715)
    plt.plot(x[:, 4], x[:, 5], '-o')
    plt.ylabel('ey')
    plt.subplot(716)
    plt.plot(x[0:-1, 4], u[:, 0], '-o')
    plt.ylabel('steering')
    plt.subplot(717)
    plt.plot(x[0:-1, 4], u[:, 1], '-o')
    plt.ylabel('acc')
    plt.show()


def plotClosedLoopColorLMPC(LMPController, map, LapToPlot):
    SS_glob = LMPController.SS_glob
    LapCounter  = LMPController.LapCounter
    SS      = LMPController.SS
    uSS     = LMPController.uSS

    TotNumberIt = LMPController.it

    print "Number iterations: ", TotNumberIt
    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((int(Points), 2))
    Points2 = np.zeros((int(Points), 2))
    Points0 = np.zeros((int(Points), 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    plt.figure()
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')

    xPlot = []
    yPlot = []
    Color = []
    for i in LapToPlot:
        for j in range(0, len(SS_glob[0:LapCounter[i], 4, i].tolist())):
            xPlot.append(SS_glob[0:LapCounter[i], 4, i].tolist()[j])
            yPlot.append(SS_glob[0:LapCounter[i], 5, i].tolist()[j])
            Color.append(np.sqrt( (SS_glob[0:LapCounter[i], 0, i].tolist()[j])**2 +  (SS_glob[0:LapCounter[i], 0, i].tolist()[j]) ) )

    plt.scatter(xPlot, yPlot, alpha=1.0, c = Color, s = 100)
    plt.xlabel("x [m]", fontsize = 16)
    plt.ylabel("y [m]", fontsize = 16)

    # plt.scatter(SS_glob[0:LapCounter[i], 4, i], SS_glob[0:LapCounter[i], 5, i], alpha=0.8, c = SS_glob[0:LapCounter[i], 0, i])
    plt.colorbar()


def plotClosedLoopLMPC(LMPController, map, LapToPlot, groupFlag):
    SS_glob = LMPController.SS_glob
    LapCounter  = LMPController.LapCounter
    SS      = LMPController.SS
    uSS     = LMPController.uSS

    TotNumberIt = LMPController.it
    print "Number iterations: ", TotNumberIt
    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((int(Points), 2))
    Points2 = np.zeros((int(Points), 2))
    Points0 = np.zeros((int(Points), 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    plt.figure()
    # plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')


    if groupFlag == 0:
        plotPoint = ['-o','-o','-o','-s','-s','k','m']
        plotColors = ['b','g','r','c','y','k','m']
        Label = LapToPlot
    elif groupFlag == 1:
        plotPoint = ['-o','-o','-o','-s','-s','k','m']
        plotColors = ['b','b','r','r','k','m']
        Label = ["LMPC", "LMPC", "Data-Based Policy", "Data-Based Policy"]
    elif groupFlag == 2:
        plotPoint = ['-o','-o','-o','-s','-s','k','m']
        plotColors = ['b','b','b','r','r','k','m']
        Label = ["LMPC", "LMPC", "LMPC", "Data-Based Policy", "Data-Based Policy"]    
    counter = 0
    for i in LapToPlot:
        if counter != 0 and (Label[counter-1] ==  Label[counter]):
            plt.plot(SS_glob[0:LapCounter[i], 4, i], SS_glob[0:LapCounter[i], 5, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        else:
            plt.plot(SS_glob[0:LapCounter[i], 4, i], SS_glob[0:LapCounter[i], 5, i], plotPoint[counter], color=plotColors[counter%len(plotColors)], label=Label[counter])
        counter += 1

    plt.legend(prop={'size': 18})
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")

    plt.figure()
    plt.subplot(711)
    counter = 0
    for i in LapToPlot:
        if counter != 0 and (Label[counter-1] ==  Label[counter]):
            plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 0, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        else:
            plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 0, i], plotPoint[counter], label=Label[counter], color=plotColors[counter%len(plotColors)])

        counter += 1
    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), borderaxespad=0, ncol=len(LapToPlot), prop={'size': 18})

    # plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.xlim([0, map.TrackLength])
    plt.ylabel('vx [m/s]', fontsize = 18)
    plt.subplot(712)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 1, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    # plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.ylabel('vy [m/s]', fontsize = 18)
    plt.subplot(713)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 2, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    # plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.xlim([0, map.TrackLength])
    plt.ylabel('wz [rad/s]', fontsize = 18)
    plt.subplot(714)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 3, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    # plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.xlim([0, map.TrackLength])
    plt.ylabel('epsi [rad]', fontsize = 18)
    plt.subplot(715)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i], 4, i], SS[0:LapCounter[i], 5, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    # plt.axvline(map.TrackLength, linewidth=4, color='g')
    plt.xlim([0, map.TrackLength])
    plt.ylabel('ey [m]', fontsize = 18)
    plt.subplot(716)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i]-1, 4, i], uSS[0:LapCounter[i] - 1, 0, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.xlim([0, map.TrackLength])
    plt.ylabel('delta [rad]', fontsize = 18)
    plt.subplot(717)
    counter = 0
    for i in LapToPlot:
        plt.plot(SS[0:LapCounter[i]-1, 4, i], uSS[0:LapCounter[i] - 1, 1, i], plotPoint[counter], color=plotColors[counter%len(plotColors)])
        counter += 1
    plt.xlim([0, map.TrackLength])
    plt.ylabel('a [m/s^2]', fontsize = 18)
    plt.xlabel('s [m]', fontsize = 18)


def animation_xy(map, LMPCOpenLoopData, LMPController, it):
    SS_glob = LMPController.SS_glob
    LapCounter = LMPController.LapCounter
    SS = LMPController.SS
    uSS = LMPController.uSS

    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((Points, 2))
    Points2 = np.zeros((Points, 2))
    Points0 = np.zeros((Points, 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    plt.figure()
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')
    plt.plot(SS_glob[0:LapCounter[it], 4, it], SS_glob[0:LapCounter[it], 5, it], '-ok', label="Closed-loop trajectory",zorder=-1)

    ax = plt.axes()
    SSpoints_x = []; SSpoints_y = []
    xPred = []; yPred = []
    SSpoints, = ax.plot(SSpoints_x, SSpoints_y, 'sb', label="SS",zorder=0)
    line, = ax.plot(xPred, yPred, '-or', label="Predicted Trajectory",zorder=1)

    v = np.array([[ 1.,  1.],
                  [ 1., -1.],
                  [-1., -1.],
                  [-1.,  1.]])
    rec = patches.Polygon(v, alpha=0.7,closed=True, fc='r', ec='k',zorder=10)
    ax.add_patch(rec)

    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)

    N = LMPController.N
    numSS_Points = LMPController.numSS_Points
    for i in range(0, int(LMPController.LapCounter[it])):

        xPred = np.zeros((N+1, 1)); yPred = np.zeros((N+1, 1))
        SSpoints_x = np.zeros((numSS_Points, 1)); SSpoints_y = np.zeros((numSS_Points, 1))

        for j in range(0, N+1):
            xPred[j,0], yPred[j,0]  = map.getGlobalPosition( LMPCOpenLoopData.PredictedStates[j, 4, i, it],
                                                             LMPCOpenLoopData.PredictedStates[j, 5, i, it] )

            if j == 0:
                x = SS_glob[i, 4, it]
                y = SS_glob[i, 5, it]
                psi = SS_glob[i, 3, it]
                l = 0.4; w = 0.2
                car_x = [ x + l * np.cos(psi) - w * np.sin(psi), x + l*np.cos(psi) + w * np.sin(psi),
                          x - l * np.cos(psi) + w * np.sin(psi), x - l * np.cos(psi) - w * np.sin(psi)]
                car_y = [ y + l * np.sin(psi) + w * np.cos(psi), y + l * np.sin(psi) - w * np.cos(psi),
                          y - l * np.sin(psi) - w * np.cos(psi), y - l * np.sin(psi) + w * np.cos(psi)]




        for j in range(0, numSS_Points):
            SSpoints_x[j,0], SSpoints_y[j,0] = map.getGlobalPosition(LMPCOpenLoopData.SSused[4, j, i, it],
                                                                     LMPCOpenLoopData.SSused[5, j, i, it])
        SSpoints.set_data(SSpoints_x, SSpoints_y)

        line.set_data(xPred, yPred)

        rec.set_xy(np.array([car_x, car_y]).T)

        plt.draw()
        plt.pause(1e-17)

def animation_states(map, LMPCOpenLoopData, LMPController, it):
    SS_glob = LMPController.SS_glob
    LapCounter = LMPController.LapCounter
    SS = LMPController.SS
    uSS = LMPController.uSS

    xdata = []; ydata = []
    fig = plt.figure()

    axvx = fig.add_subplot(3, 2, 1)
    plt.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 0, it], '-ok', label="Closed-loop trajectory")
    lineSSvx, = axvx.plot(xdata, ydata, 'sb-', label="SS")
    linevx, = axvx.plot(xdata, ydata, 'or-', label="Predicted Trajectory")
    plt.ylabel("vx")
    plt.xlabel("s")

    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)

    axvy = fig.add_subplot(3, 2, 2)
    axvy.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 1, it], '-ok')
    lineSSvy, = axvy.plot(xdata, ydata, 'sb-')
    linevy, = axvy.plot(xdata, ydata, 'or-')
    plt.ylabel("vy")
    plt.xlabel("s")

    axwz = fig.add_subplot(3, 2, 3)
    axwz.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 2, it], '-ok')
    lineSSwz, = axwz.plot(xdata, ydata, 'sb-')
    linewz, = axwz.plot(xdata, ydata, 'or-')
    plt.ylabel("wz")
    plt.xlabel("s")

    axepsi = fig.add_subplot(3, 2, 4)
    axepsi.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 3, it], '-ok')
    lineSSepsi, = axepsi.plot(xdata, ydata, 'sb-')
    lineepsi, = axepsi.plot(xdata, ydata, 'or-')
    plt.ylabel("epsi")
    plt.xlabel("s")

    axey = fig.add_subplot(3, 2, 5)
    axey.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 5, it], '-ok')
    lineSSey, = axey.plot(xdata, ydata, 'sb-')
    lineey, = axey.plot(xdata, ydata, 'or-')
    plt.ylabel("ey")
    plt.xlabel("s")

    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((Points, 2))
    Points2 = np.zeros((Points, 2))
    Points0 = np.zeros((Points, 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    axtr = fig.add_subplot(3, 2, 6)
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')
    plt.plot(SS_glob[0:LapCounter[it], 4, it], SS_glob[0:LapCounter[it], 5, it], '-ok')

    SSpoints_x = []; SSpoints_y = []
    xPred = []; yPred = []
    SSpoints_tr, = axtr.plot(SSpoints_x, SSpoints_y, 'sb')
    line_tr, = axtr.plot(xPred, yPred, '-or')

    N = LMPController.N
    numSS_Points = LMPController.numSS_Points
    for i in range(0, int(LMPController.LapCounter[it])):

        xPred    = LMPCOpenLoopData.PredictedStates[:, :, i, it]
        SSpoints = LMPCOpenLoopData.SSused[:, :, i, it]

        linevx.set_data(xPred[:, 4], xPred[:, 0])
        linevy.set_data(xPred[:, 4], xPred[:, 1])
        linewz.set_data(xPred[:, 4], xPred[:, 2])
        lineepsi.set_data(xPred[:, 4], xPred[:, 3])
        lineey.set_data(xPred[:, 4], xPred[:, 5])

        lineSSvx.set_data(SSpoints[4,:], SSpoints[0,:])
        lineSSvy.set_data(SSpoints[4,:], SSpoints[1,:])
        lineSSwz.set_data(SSpoints[4,:], SSpoints[2,:])
        lineSSepsi.set_data(SSpoints[4,:], SSpoints[3,:])
        lineSSey.set_data(SSpoints[4,:], SSpoints[5,:])

        xPred = np.zeros((N + 1, 1));yPred = np.zeros((N + 1, 1))
        SSpoints_x = np.zeros((numSS_Points, 1));SSpoints_y = np.zeros((numSS_Points, 1))

        for j in range(0, N + 1):
            xPred[j, 0], yPred[j, 0] = map.getGlobalPosition(LMPCOpenLoopData.PredictedStates[j, 4, i, it],
                                                             LMPCOpenLoopData.PredictedStates[j, 5, i, it])

        for j in range(0, numSS_Points):
            SSpoints_x[j, 0], SSpoints_y[j, 0] = map.getGlobalPosition(LMPCOpenLoopData.SSused[4, j, i, it],
                                                                       LMPCOpenLoopData.SSused[5, j, i, it])

        line_tr.set_data(xPred, yPred)
        SSpoints_tr.set_data(SSpoints_x, SSpoints_y)

        plt.draw()
        plt.pause(1e-17)

def saveGif_xyResults(map, LMPCOpenLoopData, LMPController, it):
    SS_glob = LMPController.SS_glob
    LapCounter = LMPController.LapCounter
    SS = LMPController.SS
    uSS = LMPController.uSS

    Points = int(np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4])))
    Points1 = np.zeros((Points, 2))
    Points2 = np.zeros((Points, 2))
    Points0 = np.zeros((Points, 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.halfWidth)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.halfWidth)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    fig = plt.figure()
    fig.set_tight_layout(True)
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')
    plt.plot(SS_glob[0:LapCounter[it], 4, it], SS_glob[0:LapCounter[it], 5, it], '-ok', label="Closed-loop trajectory", markersize=1,zorder=-1)

    ax = plt.axes()
    SSpoints_x = []; SSpoints_y = []
    SSpoints, = ax.plot(SSpoints_x, SSpoints_y, 'og', label="Recorded Data",zorder=0)

    v = np.array([[ 1.,  1.],
                  [ 1., -1.],
                  [-1., -1.],
                  [-1.,  1.]])
    rec = patches.Polygon(v, alpha=0.7,closed=True, fc='r', ec='k',zorder=10)
    ax.add_patch(rec)

    plt.legend(mode="expand", ncol=3)
    # plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
    #             mode="expand", borderaxespad=0, ncol=3)

    numSS_Points = LMPController.backPoints + LMPController.forePoints
    
    pdb.set_trace()

    def update(i):
        SSpoints_x = np.zeros((10*numSS_Points, 1)); SSpoints_y = np.zeros((10*numSS_Points, 1))

        x = SS_glob[i, 4, it]
        y = SS_glob[i, 5, it]
        psi = SS_glob[i, 3, it]
        l = 2*0.15;
        w = 2*0.075
        
        car_x = [x + l * np.cos(psi) - w * np.sin(psi), x + l * np.cos(psi) + w * np.sin(psi),
                 x - l * np.cos(psi) + w * np.sin(psi), x - l * np.cos(psi) - w * np.sin(psi)]
        car_y = [y + l * np.sin(psi) + w * np.cos(psi), y + l * np.sin(psi) - w * np.cos(psi),
                 y - l * np.sin(psi) - w * np.cos(psi), y - l * np.sin(psi) + w * np.cos(psi)]

        currState = SS[i, :, it]
        n = 6
        d = 2
        SS_PointSelectedTot       = np.empty((n, 0))
        uSS_PointSelectedTot      = np.empty((d, 0))
        SS_glob_PointSelectedTot  = np.empty((n, 0))
        Qfun_SelectedTot          = np.empty((0))

        for jj in range(32,38):
        # for jj in range(22,29):        
            SS_PointSelected, SS_glob_PointSelected, Qfun_Selected, uSS_PointSelected = _SelectPoints(LMPController, jj, currState)
            SS_PointSelectedTot      =  np.append(SS_PointSelectedTot, SS_PointSelected, axis=1)
            uSS_PointSelectedTot     =  np.append(uSS_PointSelectedTot, uSS_PointSelected, axis=1)
            SS_glob_PointSelectedTot =  np.append(SS_glob_PointSelectedTot, SS_glob_PointSelected, axis=1)
            Qfun_SelectedTot         =  np.append(Qfun_SelectedTot, Qfun_Selected, axis=0)

        for j in range(0, SS_glob_PointSelectedTot.shape[1]):
            SSpoints_x[j, 0] = SS_glob_PointSelectedTot[4, j]
            SSpoints_y[j, 0] = SS_glob_PointSelectedTot[5, j]

        SSpoints.set_data(SSpoints_x[0:(SS_glob_PointSelectedTot.shape[1]-1)], SSpoints_y[0:(SS_glob_PointSelectedTot.shape[1]-1)])


        rec.set_xy(np.array([car_x, car_y]).T)

    anim = FuncAnimation(fig, update, frames=np.arange(0, int(LMPController.LapCounter[it])), interval=100)

    anim.save('ClosedLoop.gif', dpi=80, writer='imagemagick')


def _SelectPoints(ZeroStepLMPC, it, x0):
    SS          = ZeroStepLMPC.SS
    SS_glob     = ZeroStepLMPC.SS_glob
    uSS         = ZeroStepLMPC.uSS
    Qfun        = ZeroStepLMPC.Qfun
    map         = ZeroStepLMPC.map
    TrackLength = map.TrackLength
    currIt      = ZeroStepLMPC.it
    LapCounter  = ZeroStepLMPC.LapCounter
    backPoints  = ZeroStepLMPC.backPoints
    forePoints  = ZeroStepLMPC.forePoints

    # x0 = np.array([x00[4]])
    # x = SS[0:(LapCounter[it]+1), 4, it]
    # print LapCounter, it
    # print SS[0:(LapCounter[it]+1), :, it]

    x = SS[0:(LapCounter[it]+1), :, it]    
    oneVec = np.ones((x.shape[0], 1))
    x0Vec = (np.dot(np.array([x0]).T, oneVec.T)).T
    diff = x - x0Vec
    
    norm = la.norm(diff, 1, axis=1)    
    MinNorm = np.argmin(norm)

    # print x0, x[MinNorm,:]

    if (MinNorm - backPoints >= 0):
        indexSSandQfun = range(-backPoints + MinNorm, -backPoints + MinNorm + forePoints)
        # SS_Points = x[shift + MinNorm:shift + MinNorm + numSS_Points, :].T
        # SS_glob_Points = x_glob[shift + MinNorm:shift + MinNorm + numSS_Points, :].T
        # Sel_Qfun = Qfun[shift + MinNorm:shift + MinNorm + numSS_Points, it]
    else:
        indexSSandQfun = range(MinNorm, MinNorm + forePoints)
        # SS_Points = x[MinNorm:MinNorm + numSS_Points, :].T
        # SS_glob_Points = x_glob[MinNorm:MinNorm + numSS_Points, :].T
        # Sel_Qfun = Qfun[MinNorm:MinNorm + numSS_Points, it]

    SS_Points      = SS[indexSSandQfun, :, it].T
    uSS_Points     = uSS[indexSSandQfun, :, it].T
    SS_glob_Points = SS_glob[indexSSandQfun, :, it].T
    Sel_Qfun       = Qfun[indexSSandQfun, it]


    # Modify the cost if the predicion has crossed the finisch line
    Sel_Qfun = Qfun[indexSSandQfun, it]
    # if xPred == []:
    #     Sel_Qfun = Qfun[indexSSandQfun, it]
    # elif (np.all((xPred[:, 4] > TrackLength) == False)):
    #     Sel_Qfun = Qfun[indexSSandQfun, it]
    # elif  it < currIt - 1:
    #     Sel_Qfun = Qfun[indexSSandQfun, it] + Qfun[0, it + 1]
    # else:
    #     sPred = xPred[:, 4]
    #     predCurrLap = LMPC.N - sum(sPred > TrackLength)
    #     currLapTime = LMPC.LapTime
    #     Sel_Qfun = Qfun[indexSSandQfun, it] + currLapTime + predCurrLap

    return SS_Points, SS_glob_Points, Sel_Qfun, uSS_Points



def Save_statesAnimation(map, LMPCOpenLoopData, LMPController, it):
    SS_glob = LMPController.SS_glob
    LapCounter = LMPController.LapCounter
    SS = LMPController.SS
    uSS = LMPController.uSS

    xdata = []; ydata = []
    fig = plt.figure()
    fig.set_tight_layout(True)

    axvx = fig.add_subplot(3, 2, 1)
    plt.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 0, it], '-ok', label="Closed-loop trajectory")
    lineSSvx, = axvx.plot(xdata, ydata, 'sb-', label="SS")
    linevx, = axvx.plot(xdata, ydata, 'or-', label="Predicted Trajectory")
    plt.ylabel("vx")
    plt.xlabel("s")

    plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)

    axvy = fig.add_subplot(3, 2, 2)
    axvy.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 1, it], '-ok')
    lineSSvy, = axvy.plot(xdata, ydata, 'sb-')
    linevy, = axvy.plot(xdata, ydata, 'or-')
    plt.ylabel("vy")
    plt.xlabel("s")

    axwz = fig.add_subplot(3, 2, 3)
    axwz.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 2, it], '-ok')
    lineSSwz, = axwz.plot(xdata, ydata, 'sb-')
    linewz, = axwz.plot(xdata, ydata, 'or-')
    plt.ylabel("wz")
    plt.xlabel("s")

    axepsi = fig.add_subplot(3, 2, 4)
    axepsi.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 3, it], '-ok')
    lineSSepsi, = axepsi.plot(xdata, ydata, 'sb-')
    lineepsi, = axepsi.plot(xdata, ydata, 'or-')
    plt.ylabel("epsi")
    plt.xlabel("s")

    axey = fig.add_subplot(3, 2, 5)
    axey.plot(SS[0:LapCounter[it], 4, it], SS[0:LapCounter[it], 5, it], '-ok')
    lineSSey, = axey.plot(xdata, ydata, 'sb-')
    lineey, = axey.plot(xdata, ydata, 'or-')
    plt.ylabel("ey")
    plt.xlabel("s")

    Points = np.floor(10 * (map.PointAndTangent[-1, 3] + map.PointAndTangent[-1, 4]))
    Points1 = np.zeros((Points, 2))
    Points2 = np.zeros((Points, 2))
    Points0 = np.zeros((Points, 2))
    for i in range(0, int(Points)):
        Points1[i, :] = map.getGlobalPosition(i * 0.1, map.width)
        Points2[i, :] = map.getGlobalPosition(i * 0.1, -map.width)
        Points0[i, :] = map.getGlobalPosition(i * 0.1, 0)

    axtr = fig.add_subplot(3, 2, 6)
    plt.plot(map.PointAndTangent[:, 0], map.PointAndTangent[:, 1], 'o')
    plt.plot(Points0[:, 0], Points0[:, 1], '--')
    plt.plot(Points1[:, 0], Points1[:, 1], '-b')
    plt.plot(Points2[:, 0], Points2[:, 1], '-b')
    plt.plot(SS_glob[0:LapCounter[it], 4, it], SS_glob[0:LapCounter[it], 5, it], '-ok')

    SSpoints_x = []; SSpoints_y = []
    xPred = []; yPred = []
    SSpoints_tr, = axtr.plot(SSpoints_x, SSpoints_y, 'sb')
    line_tr, = axtr.plot(xPred, yPred, '-or')

    N = LMPController.N
    numSS_Points = LMPController.numSS_Points

    def update(i):
        xPred    = LMPCOpenLoopData.PredictedStates[:, :, i, it]
        SSpoints = LMPCOpenLoopData.SSused[:, :, i, it]

        linevx.set_data(xPred[:, 4], xPred[:, 0])
        linevy.set_data(xPred[:, 4], xPred[:, 1])
        linewz.set_data(xPred[:, 4], xPred[:, 2])
        lineepsi.set_data(xPred[:, 4], xPred[:, 3])
        lineey.set_data(xPred[:, 4], xPred[:, 5])

        lineSSvx.set_data(SSpoints[4,:], SSpoints[0,:])
        lineSSvy.set_data(SSpoints[4,:], SSpoints[1,:])
        lineSSwz.set_data(SSpoints[4,:], SSpoints[2,:])
        lineSSepsi.set_data(SSpoints[4,:], SSpoints[3,:])
        lineSSey.set_data(SSpoints[4,:], SSpoints[5,:])

        xPred = np.zeros((N + 1, 1));yPred = np.zeros((N + 1, 1))
        SSpoints_x = np.zeros((numSS_Points, 1));SSpoints_y = np.zeros((numSS_Points, 1))

        for j in range(0, N + 1):
            xPred[j, 0], yPred[j, 0] = map.getGlobalPosition(LMPCOpenLoopData.PredictedStates[j, 4, i, it],
                                                             LMPCOpenLoopData.PredictedStates[j, 5, i, it])

        for j in range(0, numSS_Points):
            SSpoints_x[j, 0], SSpoints_y[j, 0] = map.getGlobalPosition(LMPCOpenLoopData.SSused[4, j, i, it],
                                                                       LMPCOpenLoopData.SSused[5, j, i, it])

        line_tr.set_data(xPred, yPred)
        SSpoints_tr.set_data(SSpoints_x, SSpoints_y)

    anim = FuncAnimation(fig, update, frames=np.arange(0, int(LMPController.LapCounter[it])), interval=100)

    anim.save('ClosedLoopStates.gif', dpi=80, writer='imagemagick')


main()