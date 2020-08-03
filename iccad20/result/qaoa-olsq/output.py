import glob
import csv
import ast

with open('data.csv', 'w') as data:
    datawriter = csv.writer(data, delimiter=',')
    datawriter.writerow(["size", "tket_depth", "tket_swap", "our_depth", "our_swap",
                "swap_ratio", "depth_ratio", "time", "edges"])
    for file_name in glob.glob('qaoa_exp_*'):
        print(file_name)
        dataline = dict()
        dataline["size"] = int(file_name.split('_')[-2])
        with open(file_name, 'r') as datum:
            datumlines = datum.readlines()
            our_swap = 0
            for datumline in datumlines:
                if datumline.startswith('['):
                    dataline["edges"] = ast.literal_eval(datumline)
                if datumline.startswith('num_swap'):
                    dataline["tket_swap"] = int(datumline.split(' ')[1])
                    dataline["tket_depth"] = int(datumline.split(' ')[-1].split('\\')[0])
                if datumline.startswith("A swap gate"):
                    our_swap += 1
                if datumline.startswith("final depth"):
                    dataline["our_depth"] = int(datumline.split(' ')[-1].split('\\')[0])
                if datumline.startswith("Compilation time"):
                    dataline["time"] = str(datumline.split(' ')[-1])[:-2]
                dataline['our_swap'] = our_swap
            print(dataline)
            datawriter.writerow([dataline["size"], dataline["tket_depth"],
                        dataline["tket_swap"], dataline["our_depth"], dataline["our_swap"],
                        dataline["tket_swap"] / dataline["our_swap"],
                        dataline["tket_depth"] / dataline["our_depth"],
                        dataline["time"], dataline["edges"]])
        datum.close()
data.close()
