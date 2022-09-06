class Config:

        """
        Config is just a central class for all of the modules where settings which are common can be tweaked or changed.
        """

        # Serial port config settings
        port = 'COM9'
        baud_rate = 115200
        buffer_size = 100000

        # Plotting settings
        plot_size = 200
        dt = 1/20

        labels = {

                "0":'Time [s]',
                "1":'Temperature',

                "2":'Acceleration (x)',
                "3":'Acceleration (y)',
                "4":'Acceleration (z)',

                "5":'Angular Velocity (x)',
                "6":'Angular Velocity (y)',
                "7":'Angular Velocity (z)',

                "8":'Jerk (x)',
                "9":'Jerk (y)',
                "10":'Jerk (z)',

                "11":'Norm(Acceleration)',
                "12":'Norm(Angular Velocity)',
                "13":'Norm(Jerk)',

                "14":'Filtered Velocity (x)',
                "15":'Filtered Velocity (y)',
                "16":'Filtered Velocity (z)',

                "17":'Filtered Acceleration (x)',
                "18":'Filtered Acceleration (y)',
                "19":'Filtered Acceleration (z)',

                "20":'Filtered Angular Velocity (x)',
                "21":'Filtered Angular Velocity (y)',
                "22":'Filtered Angular Velocity (z)',

                "23":'Filtered Jerk (x)',
                "24":'Filtered Jerk (y)',
                "25":'Filtered Jerk (z)',

                "26":'Filtered Norm(Velocity)',
                "27":'Filtered Norm(Acceleration)',
                "28":'Filtered Norm(Angular Velocity)',
                "29":'Filtered Norm(Jerk)',

                "30":'Smoothed Velocity (x)',
                "31":'Smoothed Velocity (y)',
                "32":'Smoothed Velocity (z)',

                "33":'Smoothed Acceleration (x)',
                "34":'Smoothed Acceleration (y)',
                "35":'Smoothed Acceleration (z)',

                "36":'Smoothed Angular Velocity (x)',
                "37":'Smoothed Angular Velocity (y)',
                "38":'Smoothed Angular Velocity (z)',

                "39":'Smoothed Jerk (x)',
                "40":'Smoothed Jerk (y)',
                "41":'Smoothed Jerk (z)',

                "42":'Smoothed Norm(Velocity)',
                "43":'Smoothed Norm(Acceleration)',
                "44":'Smoothed Norm(Angular Velocity)',
                "45":'Smoothed Norm(Jerk)',

        }

        categories = {
                     'raw': {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13},
                     'filter': {14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29},
                     'smooth': {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45},

                     'x': {2, 5, 8, 14, 17, 20, 23, 30, 33, 36, 39},
                     'y': {3, 6, 9, 15, 18, 21, 24, 31, 34, 37, 40},
                     'z': {4, 7, 10, 16, 19, 22, 25, 32, 35, 38, 41},
                     'norm': {11, 12, 13, 26, 27, 28, 29, 42, 43, 44, 45},

                     'vel': {14, 15, 16, 26, 30, 31, 32, 42},
                     'acc': {2, 3, 4, 11, 17, 18, 19, 27, 33, 34, 35, 43},
                     'ang': {5, 6, 7, 12, 20, 21, 22, 28, 36, 37, 38, 24},
                     'jerk': {8, 9, 10, 13, 23, 24, 25, 29, 39, 40, 41, 45},

                     'temp':{1},
                     'all': {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,14, 15, 16, 17, 18, 19,
                             20, 21, 22, 23, 24, 25, 26, 27, 28, 29,30, 31, 32, 33, 34, 35, 36,
                             37, 38, 39, 40, 41, 42, 43, 44, 45}
        }
        pen = [
                (237, 12, 12),
                (19, 12, 237),
                (237, 94, 12),
                (12, 230, 237),
                (237, 169, 12),
                (12, 237, 151),
                (218, 237, 12),
                (12, 237, 68),
                (106, 237, 12),
        ]
