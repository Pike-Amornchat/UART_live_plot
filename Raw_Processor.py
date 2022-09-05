from Modules import *


class Raw_Processor(QThread):

    raw_processor_to_application_carrier = Signal(list)
    raw_processor_to_storage_carrier = Signal(list)
    raw_processor_to_plotter_carrier = Signal(list)

    def __init__(self,data_manager=None):
        super(Raw_Processor, self).__init__()

        self.data_manager = data_manager

        self.data_manager.covariance_carrier.connect(self.receive_covariance)
        self.data_manager.manager_to_raw_processor_carrier.connect(self.receive_data)

        self.init_raw_processor()

    def init_raw_processor(self):

        # Initializing variables
        self.R = []
        self.cov_acc = []
        self.cov_ang = []
        self.cov_buffer = []
        self.data_buffer = []

        # Kalman variables - all 2D Numpy arrays (matrices)
        self.zk = np.zeros((6,1))
        self.x_current = np.zeros((9,1))
        self.P_current = np.zeros((9,9))
        self.Fk = np.zeros((9,9))
        self.Bk = 0
        self.uk = 0
        self.Hk = 0
        self.Qk = 0
        self.Rk = 0

        # Raw data buffer - list of 14 ring buffers
        self.data = [Dynamic_RingBuff(Config.plot_size + 2) for i in range(46)]

        # Init 2 zeros at the back of the array for the jerk - we will only plot [2:] anyway.

        for i in Config.categories['jerk']:
            self.data[i].add(0)
            self.data[i].add(0)

        # Ring buffer for Kalman Smoother - list of 2D numpy arrays (list of matrices)
        self.x_prior = Dynamic_RingBuff(Config.plot_size + 2)
        self.x_now = Dynamic_RingBuff(Config.plot_size + 2)
        self.P_prior = Dynamic_RingBuff(Config.plot_size + 2)
        self.P_now = Dynamic_RingBuff(Config.plot_size + 2)
        self.x_smoothed = []

        # Time and temperature buffers - list of float
        self.time = Dynamic_RingBuff(Config.plot_size + 2)
        self.temp = Dynamic_RingBuff(Config.plot_size + 2)

    def reset(self):
        self.init_raw_processor()

    def init_kalman(self, dt, cov_acc, cov_ang, Rk_estimate):

        # Initialize filter with x_0 = 0 - 2D array of 1xn
        x_current = np.transpose(np.asarray([[0 for i in range(9)]]))

        # Initialize covariance matrix of error - assume identity
        P_current = np.zeros((9, 9)) + 1

        # Set up Fk - Acceleration stays the same, and angular velocity stays the same
        Fk = np.asarray([[1, 0, 0, dt, 0, 0, 0, 0, 0],
                         [0, 1, 0, 0, dt, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, dt, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 1, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 1]])

        # # Default 0 acceleration
        # Fk = np.asarray([[1, 0, 0, dt, 0, 0, 0, 0, 0],
        #                  [0, 1, 0, 0, dt, 0, 0, 0, 0],
        #                  [0, 0, 1, 0, 0, dt, 0, 0, 0],
        #                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                  [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                  [0, 0, 0, 0, 0, 0, 1, 0, 0],
        #                  [0, 0, 0, 0, 0, 0, 0, 1, 0],
        #                  [0, 0, 0, 0, 0, 0, 0, 0, 1]])

        # Set up Bk - in case it is 0 (identity x 0 = 0)

        Bk = np.identity(9)

        # Set up uk, it will also be 0

        uk = np.transpose(np.asarray([[0 for i in range(9)]]))

        # Set up the sensor conversion Hk - in this case it is a 6x9 matrix, as there are 6 readings and 9 state variables

        Hk = np.asarray([[0, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 1, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0, 1]])

        #  Set up Qk - Physical noise covariance matrix
        Qk = np.asarray([[(dt ** 2) * (cov_acc[0][0] ** 2), (dt ** 2) * (cov_acc[1][0] ** 2),
                          (dt ** 2) * (cov_acc[2][0] ** 2), dt * cov_acc[0][0], dt * cov_acc[1][0], dt * cov_acc[2][0],
                          0, 0, 0],
                         [(dt ** 2) * (cov_acc[1][0] ** 2), (dt ** 2) * (cov_acc[1][1] ** 2),
                          (dt ** 2) * (cov_acc[2][1] ** 2), dt * cov_acc[1][0], dt * cov_acc[1][1], dt * cov_acc[2][1],
                          0, 0, 0],
                         [(dt ** 2) * (cov_acc[1][0] ** 2), (dt ** 2) * (cov_acc[2][1] ** 2),
                          (dt ** 2) * (cov_acc[2][2] ** 2), dt * cov_acc[0][2], dt * cov_acc[1][2], dt * cov_acc[2][2],
                          0, 0, 0],
                         [dt * cov_acc[0][0], dt * cov_acc[0][1], dt * cov_acc[0][2], cov_acc[0][0], cov_acc[1][0],
                          cov_acc[2][0], 0, 0, 0],
                         [dt * cov_acc[1][0], dt * cov_acc[1][1], dt * cov_acc[1][2], cov_acc[1][0], cov_acc[1][1],
                          cov_acc[2][1], 0, 0, 0],
                         [dt * cov_acc[2][0], dt * cov_acc[2][1], dt * cov_acc[2][2], cov_acc[2][0], cov_acc[1][2],
                          cov_acc[2][2], 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, cov_ang[0][0], cov_ang[0][1], cov_ang[0][2]],
                         [0, 0, 0, 0, 0, 0, cov_ang[1][0], cov_ang[1][1], cov_ang[1][2]],
                         [0, 0, 0, 0, 0, 0, cov_ang[2][0], cov_ang[2][1], cov_ang[2][2]]])

        # Add offset to prevent non-invertible

        add_noise_acc = np.asarray([[1, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])
        add_noise_ang = np.asarray([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1]])

        Qk = Qk * 3

        # Rk is taken into account already by the MCU calibration sequence,
        # but a scale factor adjustment can be applied here

        Rk = (Rk_estimate * 5 + add_noise_acc * 0.1 + add_noise_ang * 0.05) * 2

        return x_current, P_current, Fk, Bk, uk, Hk, Qk, Rk

    def kalman_filter(self,x_before, P_before, Fk, Bk, uk, Hk, Qk, Rk, zk):

        import numpy as np

        # Predict:

        x_predict = np.dot(Fk, x_before) + np.dot(Bk, uk)
        P_predict = np.dot(Fk, np.dot(P_before, np.transpose(Fk))) + Qk

        # Update:
        ik = zk - np.dot(Hk, x_predict)

        Sk = np.dot(Hk, np.dot(P_predict, np.transpose(Hk))) + Rk

        Kk = np.dot(np.dot(P_predict, np.transpose(Hk)), np.linalg.inv(Sk))

        x_current = x_predict + np.dot(Kk, ik)

        IKH = np.identity(len(P_before)) - np.dot(Kk, Hk)
        P_current = np.dot(np.dot(IKH, P_predict), np.transpose(IKH)) \
                    + np.dot(np.dot(Kk, Rk), np.transpose(Kk))

        return x_predict, x_current, P_predict, P_current

    def kalman_smoother(self,x_prior, x_now, P_prior, P_now, Fk):
        N = len(x_prior)

        x_smooth = [[] for p in range(N)]
        x_smooth[-1] = x_now[-1]
        P_smooth = [[] for q in range(N)]
        P_smooth[-1] = P_now[-1]

        for k in range((N - 2), -1, -1):
            L = np.dot(np.dot(P_now[k], Fk.T), np.linalg.inv(P_prior[k + 1]))
            x_smooth[k] = x_now[k] + np.dot(L, x_smooth[k + 1] - x_prior[k + 1])
            P_smooth[k] = P_now[k] + np.dot(np.dot(L, P_smooth[k + 1] - P_prior[k + 1]), L.T)

        final = np.zeros((len(P_smooth[0]), N))
        for i in range(N):
            for j in range(len(final)):
                final[j][i] = x_smooth[i][j][0]

        return final

    def receive_data(self,input_buffer=''):
        self.data_buffer.append(input_buffer)
        self.calculate()

    def receive_covariance(self,input_buffer=''):
        self.cov_buffer.append(input_buffer)
        self.R = np.asarray(self.cov_buffer[0][0])
        self.cov_acc = np.asarray(self.cov_buffer[0][1])
        self.cov_ang = np.asarray(self.cov_buffer[0][2])
        self.x_current, self.P_current, self.Fk, self.Bk, self.uk, \
        self.Hk, self.Qk, self.Rk = self.init_kalman(Config.dt, self.cov_acc, self.cov_ang, self.R)

    def calculate(self):
        # 0 - 7 updated (time, temp, raw acc, raw ang)

        # Append time
        self.data[0].add(self.data_buffer[0][0])

        # Append temperature
        self.data[1].add(self.data_buffer[0][1])

        # Save zk
        self.zk = np.transpose(np.asarray([self.data_buffer[0][2:7+1]]))
        for i in range(2,7 + 1):
            self.data[i].add(self.data_buffer[0][i])

        # Calculate jerk and update 8 - 10:
        if len(self.data[2].buffer) >= 3:
            for i in range(2, 4 + 1):
                self.data[6+i].add((3 * self.data[i].buffer[-1] - 4 * self.data[i].
                                    buffer[-2] + self.data[i].buffer[-3])
                                      / (2 * Config.dt))

        # Update 11 - 12, the norms of angular and acceleration raw
        self.data[11].add(self.data_buffer[0][8])
        self.data[12].add(self.data_buffer[0][9])

        # Calculate the norm of the jerk raw (13):
        self.data[13].add(np.sqrt(self.data[8].buffer[-1]**2+self.data[9].buffer[-1]**2+self.data[10].
                                  buffer[-1]**2))

        # Clear the data buffer
        self.data_buffer = self.data_buffer[1:]

        # Now begins the calculations:

        self.x_before, self.x_current, self.P_before, self.P_current = self.kalman_filter(self.x_current,
                                                                                          self.P_current,
                                                                                          self.Fk, self.Bk,
                                                                                          self.uk, self.Hk,
                                                                                          self.Qk, self.Rk,
                                                                                          self.zk)

        # 14 - 22 updated

        # Add the filtered x to the array for plotting (2D array 46 x N+2)
        for i in range(14,22 + 1):
            self.data[i].add(self.x_current[i-14][0])

        # Calculate the filtered norm and update 26 - 28 (without jerk):
        for i in range(3):
            self.data[26 + i].add(
                np.sqrt(self.data[(14 + 3 * i) + 0].buffer[-1] ** 2 + self.data[(14 + 3 * i) + 1].buffer[-1]
                        ** 2 + self.data[(14 + 3 * i) + 2].buffer[-1] ** 2))

        # Calculate jerk and update 23 - 25, 29:
        if len(self.data[17].buffer) >= 3:
            for i in range(17, 19 + 1):
                self.data[6 + i].add((3 * self.data[i].buffer[-1] - 4 *
                                      self.data[i].buffer[-2] + self.data[i].buffer[-3])
                                        / (2 * Config.dt))

            # Calculate the filtered norm jerk (29):
            self.data[29].add(
                np.sqrt(self.data[23].buffer[-1] ** 2 + self.data[24].buffer[-1]
                        ** 2 + self.data[25].buffer[-1] ** 2))

        # Add the rest into the Kalman smoother arrays

        self.x_prior.add(self.x_before)
        self.x_now.add(self.x_current)
        self.P_prior.add(self.P_before)
        self.P_now.add(self.P_current)

        # Apply Kalman smoothing (30 - 38)
        self.x_smoothed = self.kalman_smoother(self.x_prior.buffer,
                                               self.x_now.buffer,
                                               self.P_prior.buffer, self.P_now.buffer, self.Fk)

        # Add the smoothed x to the array for plotting (2D array 46 x N+2)
        for i in range(30, 38 + 1):
            self.data[i].add(self.x_smoothed[i-30][0])

        # Calculate the filtered norm and update 42 - 44:
        for i in range(3):
            self.data[42 + i].add(
                np.sqrt(self.data[(30 + 3 * i) + 0].buffer[-1] ** 2 + self.data[(30 + 3 * i) + 1].buffer[-1]
                        ** 2 + self.data[(30 + 3 * i) + 2].buffer[-1] ** 2))

        # Calculate jerk and update 39 - 41, 45:
        if len(self.data[33].buffer) >= 3:
            for i in range(33, 35 + 1):
                self.data[6 + i].add((3 * self.data[i].buffer[-1] - 4 *
                                      self.data[i].buffer[-2] + self.data[i].buffer[-3])
                                        / (2 * Config.dt))

            # Calculate the smoothed jerk norm (45)
            self.data[45].add(
                np.sqrt(self.data[39].buffer[-1] ** 2 + self.data[40].buffer[-1]
                        ** 2 + self.data[41].buffer[-1] ** 2))

        # Once everything is calculated and we have a steady stream going, send the latest data over:
        if len(self.data[2].buffer) >= 3:

            send = []
            send_str = []
            for i in range(len(self.data)):
                send.append(self.data[i].buffer[-1])
                send_str.append(str(self.data[i].buffer[-1]))

            # self.raw_processor_to_application_carrier.emit(send)
            # self.raw_processor_to_plotter_carrier.emit(send)
            self.raw_processor_to_storage_carrier.emit(send_str)
