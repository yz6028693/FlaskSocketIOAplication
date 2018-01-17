# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_socketio import emit, SocketIO
import eventlet
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_handlers=True)
import numpy as np
from math import pi, sqrt
import multiprocessing as mp


# Archimedean Spiral with Evolution Strategy
# The main goal of this small demo is to create points (red points) with Evolution Strategy algorithm
# to get close to every random points (blue points) created from Archimedean Spiral curve.

class ESGradientExplorer(object):

    def __init__(self):

        self.Pop_Size = 100  # Number of popuNlation size.


    # Function to transfer polar coordinate system to Cartesian coordinate system. （regular coordinate system）
    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return (x, -y)


    def InitPoint(self, nums):
        InitPoint = np.random.uniform(low=-6, high=6, size=(nums,2))
        return InitPoint


    def KidsWithNoise(self, CenterPoint, sigma):
        CenterPoint = np.expand_dims(CenterPoint, 0)
        noise =  np.random.randn(self.Pop_Size, 2)
        kidswithnoise = CenterPoint.repeat(self.Pop_Size, axis=0) + sigma * noise
        return kidswithnoise, noise


    # Function to calculate the fitness (parameter we based on to define which individuals are better) of each individual (last and this generation).
    # The goal of our population (red points) is to get close to the blue points.
    # Since I think the blue points as different planets, I used the gravitation equation to calculate the fitness. Salute to Isaac Newton.
    def get_rewards(self, kidswithnoise, XYList):

        Gravity = np.zeros(self.Pop_Size)

        for n in range(len(XYList[0])):
            # Think the blue points as different planet, as a result, I choose to use the gravitation equation to differ the fitness, 6.674 is the gravitational constant.
            Gravity += 6.674 / (
            (kidswithnoise[:, 0] - XYList[0][n]) ** 2 + (kidswithnoise[:, 1] - XYList[1][n]) ** 2)

        NormalizedGravity = (Gravity - np.mean(Gravity)) / np.std(Gravity)

        return NormalizedGravity


    def UpdateCenterPoint(self, CenterPoint, NormalizedRewards, noise, alpha, sigma):

        updatedCenterPoint = CenterPoint + alpha/(self.Pop_Size * sigma) * np.dot(noise.T, NormalizedRewards)

        return updatedCenterPoint


    def ArrayCheckExist(self, CenterPoint, FinishedList):
        for item in FinishedList:
            if CenterPoint.all == item.all:
                return False
        return True


    # Remove occupied blue points from target points list
    def UpdateXYList(self, CenterPoints, XYList, FinishedList):
        deleteI = []
        for i in range(len(XYList[0])):
            for CenterPoint in CenterPoints:
                # If a red point is close enough to a blue point, we will not add the Gravity of this blue point to the fitness. (It will lose it attraction to red points)
                if sqrt(((CenterPoint[0] - XYList[0][i]) ** 2 + (CenterPoint[1] - XYList[1][i]) ** 2)) < 0.01:
                    if self.ArrayCheckExist(CenterPoint, FinishedList):
                        FinishedList.append(CenterPoint)
                    if i not in deleteI:
                        deleteI.append(i)
                    break
        if len(deleteI) != 0:
            XYList[0] = np.delete(XYList[0], deleteI)
            XYList[1] = np.delete(XYList[1], deleteI)
        return FinishedList, XYList


    def WorkFlow(self, CenterPoint, XYList, sigma, alpha):
        kidswithnoise, noise = self.KidsWithNoise(CenterPoint, sigma)
        NormalizedRewards = self.get_rewards(kidswithnoise, XYList)
        updatedCenterPoint = self.UpdateCenterPoint(CenterPoint, NormalizedRewards, noise, alpha, sigma)
        return updatedCenterPoint, kidswithnoise



    # Function to create random points from Archimedean Spiral curve.
    def RandomPoints(self, num):
        phi1inx = np.random.choice(np.arange(540), size=num, replace=False)
        phi1 = [i * (2 * pi / 360) for i in phi1inx]
        rho1 = np.multiply(phi1, 0.5)
        x_1, y_1 = self.pol2cart(rho1, phi1)
        return [x_1, y_1]


    # Function to create data for ploting Archimedean Spiral curve.
    def PlotArchimedeanSpiral(self):
        phi = [2 * i * (2 * pi / 360) for i in range(270)]
        rho1 = np.multiply(phi, 0.5)
        x_1, y_1 = self.pol2cart(rho1, phi)
        return [x_1, y_1]

triggers = {}

@socketio.on('client_connected')
def handle_client_connect_event(json):
    global triggers
    print("New Client connected at: " + str(time.asctime(time.localtime(time.time()))))
    tool = ESGradientExplorer()
    XYList1 = tool.PlotArchimedeanSpiral()
    x1 = list(XYList1[0])
    y1 = list(XYList1[1])
    nameSpace = str(json['namespace'])
    triggers[nameSpace] = 0
    emit('Init', {'X': x1, 'Y': y1})
    print('triggers: ', triggers)




@socketio.on('trigger', namespace='/trigger')
def handle_trigger(json):
    global triggers
    triggers[str(json['namespace'])] = 1


@socketio.on('create_figure_button')
def handle_create_figure_button(json):
    global triggers
    namespace = str(json['namespace'])
    if triggers[namespace] == 1:
        triggers[namespace] = 0
    tool = ESGradientExplorer()
    FinishedList = []
    N_workers = int(json['ExplorersNum'])
    timeout = float(json['UpdateSpeed'])
    XYList = tool.RandomPoints(40)
    x2 = list(XYList[0])
    y2 = list(XYList[1])
    emit('RandomPoints', {'X': x2, 'Y': y2})
    pool = mp.Pool(N_workers)
    sigmas = np.random.uniform(low=0.03, high=0.06, size=(N_workers))
    alphas = np.random.uniform(low=0.008, high=0.01, size=(N_workers))
    InitPoints = tool.InitPoint(N_workers)
    CenterPoints = InitPoints

    print('Number of Explorers: {0}'.format(str(json)))

    colors = ['cyan', 'purple', 'green', 'orange', 'blue', 'yellow', 'black', 'white']
    explorersname = ['Explorer1', 'Explorer2', 'Explorer3', 'Explorer4', 'Explorer5', 'Explorer6', 'Explorer7',
                     'Explorer8']

    generation = 0
    while len(XYList[0]) != 0:
        if triggers[namespace] == 1:
            break
        generation += 1
        # if generation % 5 ==0:
        #     sigmas[0] += 0.01
        #     alphas[0] += 0.002
        explorers = [pool.apply_async(tool.WorkFlow, (CenterPoints[i], XYList, sigmas[i], alphas[i]))
                     for i in range(N_workers)]
        PoolReturns = [returns.get() for returns in explorers]
        updatedCenterPoints = [explorer[0] for explorer in PoolReturns]
        Differentkidswithnoise = [explorer[1] for explorer in PoolReturns]
        i = 0
        for kidswithnoise in Differentkidswithnoise:
            Kidsx = list(kidswithnoise[:, 0])
            Kidsy = list(kidswithnoise[:, 1])
            Kidscolor = [colors[i]] * len(list(kidswithnoise[:, 0]))
            emit('KidsData', {'X': Kidsx, 'Y': Kidsy, 'Color': Kidscolor, 'Refresh': i})
            i += 1
        Centerx = []
        Centery = []
        Centercolor = []
        Centerlegend = []
        i = 0
        for CenterPoint in list(CenterPoints):
            Centerx += [CenterPoint[0]]
            Centery += [CenterPoint[1]]
            Centercolor += [colors[i]]
            Centerlegend += [explorersname[i]]
            i += 1
        CenterPoints = np.vstack([updatedCenterPoint for updatedCenterPoint in updatedCenterPoints])
        FinishedList, XYList = tool.UpdateXYList(CenterPoints, XYList, FinishedList)
        if len(FinishedList) != 0:
            ArrayFinishedList = np.array(FinishedList)
            Finishedx = list(ArrayFinishedList[:, 0])
            Finishedy = list(ArrayFinishedList[:, 1])
            emit('FinishedData', {'X': Finishedx, 'Y': Finishedy})
        emit('CenterData', {'X': Centerx, 'Y': Centery, 'Color': Centercolor, 'Legend': Centerlegend})
        eventlet.sleep(timeout)
    if triggers[namespace] == 0:
        print('Finished!')
        print(generation)
    else:
        print('Restarted')
        print(generation)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, port=5000)