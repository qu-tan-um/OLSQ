class qcdevice:
    def __init__(self, name):
        if name == "aspen4":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                        (0, 8), (3, 11), (4, 12), (7, 15),
                        (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15)]
            self.fidelity_measurement = [0.928 for _ in range(16)]
            self.fidelity_single_qubit = [0.999 for _ in range(16)]
            self.fidelity_two_qubit = [0.955 for _ in range(18)]
        elif name == "sycamore23":
            self.swap_duration = 1
            self.count_physical_qubit = 23
            self.connection_list = [(0, 2), (1, 2), (2, 3), (1, 5), (2, 6), (3, 7),
                                    (4, 5), (5, 6), (6, 7), (7, 8),
                                    (4, 10), (5, 11), (6, 12), (7, 13),
                                    (9, 10), (10, 11), (11, 12), (12, 13),
                                    (9, 15), (10, 16), (11, 17), (12, 18),
                                    (14, 15), (15, 16), (16, 17), (17, 18),
                                    (15, 19), (16, 20), (17, 21), (19, 20), (20, 21), (20, 22)]
        elif name =="grid2by3":
            self.swap_duration = 3
            self.count_physical_qubit = 6
            self.connection_list = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5)]
            self.fidelity_measurement = [0.928 for _ in range(6)]
            self.fidelity_single_qubit = [0.999 for _ in range(6)]
            self.fidelity_two_qubit = [0.955 for _ in range(7)]
        elif name == "sycamore3by2":
            self.swap_duration = 1
            self.count_physical_qubit = 6
            self.connection_list = [(0, 1), (0, 4), (1, 2), (1, 5), (3, 4), (4, 5)]
        elif name == "sycamore4by2":
            self.swap_duration = 1
            self.count_physical_qubit = 8
            self.connection_list = [(0, 1), (1, 2), (2, 3), (0, 5), (1, 6), (2, 7), (4, 5), (5, 6), (6, 7)]
        elif name == "sycamore5by2":
            self.swap_duration = 1
            self.count_physical_qubit = 10
            self.connection_list = [(0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 6), (5, 6), (5, 7), (6, 8), (7, 8), (7, 9)]
        elif name =="grid2by3plus":
            self.swap_duration = 3
            self.count_physical_qubit = 7
            self.connection_list = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5), (5, 6)]
        elif name == "grid2by4":
            self.swap_duration = 3
            self.count_physical_qubit = 8
            self.connection_list = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7)]
            self.fidelity_measurement = [0.928 for _ in range(8)]
            self.fidelity_single_qubit = [0.999 for _ in range(8)]
            self.fidelity_two_qubit = [0.955 for _ in range(10)]
        elif name == "tokyopart1":
            self.swap_duration = 3
            self.count_physical_qubit = 8
            self.connection_list = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (1, 6), (2, 5), (2, 6), (3, 7), (4, 5), (5, 6), (6, 7)]
        elif name == "tokyopart2":
            self.swap_duration = 3
            self.count_physical_qubit = 8
            self.connection_list = [(0, 1), (1, 2), (2, 3), (0, 4), (0, 5), (1, 4), (1, 5), (2, 6), (2, 7), (3, 6), (3, 7), (4, 5), (5, 6), (6, 7)]
        elif name =="Sycamore":
            self.swap_duration = 3
            self.count_physical_qubit = 54
            self.connection_list = [(0, 6), (1, 6), (1, 7), (2, 7), (2, 8), (3, 8), (3, 9), (4, 9), (4, 10), (5, 10), (5, 11),
                                    (6, 12), (6, 13), (7, 13), (7, 14), (8, 14), (8, 15), (9, 15), (9, 16), (10, 16), (10, 17), (11, 17),
                                    (12, 18), (13, 18), (13, 19), (14, 19), (14, 20), (15, 20), (15, 21), (16, 21), (16, 22), (17, 22), (17, 23),
                                    (18, 24), (18, 25), (19, 25), (19, 26), (20, 26), (20, 27), (21, 27), (21, 28), (22, 28), (22, 29), (23, 29),
                                    (24, 30), (25, 30), (25, 31), (26, 31), (26, 32), (27, 32), (27, 33), (28, 33), (28, 34), (29, 34), (29, 35),
                                    (30, 36), (30, 37), (31, 37), (31, 38), (32, 38), (32, 39), (33, 39), (33, 40), (34, 40), (34, 41), (35, 41),
                                    (36, 42), (37, 42), (37, 43), (38, 43), (38, 44), (39, 44), (39, 45), (40, 45), (40, 46), (41, 46), (41, 47),
                                    (42, 48), (42, 49), (43, 49), (43, 50), (44, 50), (44, 51), (45, 51), (45, 52), (46, 52), (46, 53), (47, 53)]
        elif name == "Ourense":
            self.swap_duration = 3
            self.count_physical_qubit = 5
            self.connection_list = [(0, 1), (1, 2), (1, 3), (3, 4)]
        elif name == "Tokyo":
            self.swap_duration = 3
            self.count_physical_qubit = 20
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4),
                      (0, 5), (1, 6), (1, 7), (2, 6), (2, 7), (3, 8), (3, 9), (4, 8), (4, 9),
                      (5, 6), (6, 7), (7, 8), (8, 9),
                      (5, 10), (5, 11), (6, 10), (6, 11), (7, 12), (7, 13), (8, 12), (8, 13), (9, 14),
                      (10, 11), (11, 12), (12, 13), (13, 14),
                      (10, 15), (11, 16), (11, 17), (12, 16), (12, 17), (13, 18), (13, 19), (14, 18), (14, 19),
                      (15, 16), (16, 17), (17, 18), (18, 19)]
        elif name == "ibmq16":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                                   (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15),
                                   (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15)]
        elif name == "ibmq14":
            self.swap_duration = 3
            self.count_physical_qubit = 14
            self.connection_list = [(5, 4), (2, 3), (11, 3), (4, 3), (5, 9), (11, 12),
                                    (13, 1), (11, 10), (13, 12), (6, 8), (1, 0), (9, 10),
                                    (1, 2), (7, 8), (12, 2), (4, 10), (5, 6), (9, 8)]
            self.fidelity_single_qubit = [0.996757189527604,
                                          0.9793793725978255,
                                          0.9897185653226979,
                                          0.9987609056484434,
                                          0.9964841388928687,
                                          0.9916932994004406,
                                          0.9848184244233908,
                                          0.9833042956834309,
                                          0.9978444026534106,
                                          0.9925626580199498,
                                          0.9914763338475653,
                                          0.99580965731764,
                                          0.9969675362043758,
                                          0.8793886441600057]
            self.fidelity_measurement = [0.9691000000000001,
                                         0.9681,
                                         0.9647,
                                         0.7399,
                                         0.9715,
                                         0.9373,
                                         0.9671000000000001,
                                         0.5325,
                                         0.9648,
                                         0.8425,
                                         0.7686,
                                         0.9556,
                                         0.9376,
                                         0.8989]
            self.fidelity_two_qubit = [0.9500415764843599,
                                       0.9574552240406733,
                                       0.9571530007346793,
                                       0.9439360238197881,
                                       0.861262453129556,
                                       0.9551420419704448,
                                       0.6611596066648988,
                                       0.39959221674416556,
                                       0.7455161999254012,
                                       0.9611064583395956,
                                       0.9555453046248608,
                                       0.9152715894185248,
                                       0.9306612972854601,
                                       0.6615054815895598,
                                       0.9019897225982896,
                                       0.9515933858380659,
                                       0.9379522648979998,
                                       0.9457406533540407]

        elif name == "ibmqx2":
            self.swap_duration = 3
            self.count_physical_qubit = 5
            self.connection_list = [[0,1],[0,2],[1,2],[2,3],[2,4],[3,4]]
            self.fidelity_two_qubit = [0.971324125855421,
                                       0.9728188875810317,
                                       0.9632801476247475,
                                       0.9347599759334276,
                                       0.9356666889085882,
                                       0.9502316716169495]
            self.fidelity_measurement = [0.846, 0.937, 0.962, 0.97, 0.926]
            self.fidelity_single_qubit = [0.9992273692706546,
                                          0.9988839145121239,
                                          0.9989697818583652,
                                          0.9984545411897114,
                                          0.9987121725030761]
        elif name =="linear3":
            self.swap_duration = 3
            self.count_physical_qubit = 3
            self.connection_list = [(0, 1), (1, 2)]
        elif name == "Agave":
            self.swap_duration = 3
            self.count_physical_qubit = 4
            self.connection_list = [(0, 1), (1, 2), (2, 3)]
        elif name == "1a":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                                    (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15),
                                    (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15)]
        elif name == "2a":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                                    (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15),
                                    (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15),
                                    (0, 9), (1, 8), (2, 11), (3, 10), (4, 13), (5, 12), (6, 15), (7, 14)]
        elif name == "2b":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                                    (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15),
                                    (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15),
                                    (1, 8), (1, 10), (3, 10), (3, 12), (5, 12), (5, 14), (7, 14)]
        elif name == "1b":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3),
                                    (0, 4), (1, 5), (2, 6), (3, 7),
                                    (4, 5), (5, 6), (6, 7),
                                    (4, 8), (5, 9), (6, 10), (7, 11),
                                    (8, 9), (9, 10), (10, 11),
                                    (8, 12), (9, 13), (10, 14), (11, 15),
                                    (12, 13), (13, 14), (14, 15)]
        elif name == "3a":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3),
                                    (0, 4), (1, 5), (2, 6), (3, 7),
                                    (4, 5), (5, 6), (6, 7),
                                    (4, 8), (5, 9), (6, 10), (7, 11),
                                    (8, 9), (9, 10), (10, 11),
                                    (8, 12), (9, 13), (10, 14), (11, 15),
                                    (12, 13), (13, 14), (14, 15),
                                    (0, 5), (1, 4), (2, 7), (3, 6),
                                    (5, 10), (6, 9),
                                    (8, 13), (9, 12), (10, 15), (11, 14)]
        elif name == "3b":
            self.swap_duration = 3
            self.count_physical_qubit = 16
            self.connection_list = [(0, 1), (1, 2), (2, 3),
                                    (0, 4), (1, 5), (2, 6), (3, 7),
                                    (4, 5), (5, 6), (6, 7),
                                    (4, 8), (5, 9), (6, 10), (7, 11),
                                    (8, 9), (9, 10), (10, 11),
                                    (8, 12), (9, 13), (10, 14), (11, 15),
                                    (12, 13), (13, 14), (14, 15),
                                    (0, 5), (2, 5), (2, 7),
                                    (4, 9), (6, 9), (6, 11),
                                    (8, 13), (10, 13), (10, 15)]
        else:
            self.swap_duration = 0
            self.count_physical_qubit = 0
            self.connection_list = []
