import re
import os


def readfile(filename):
    print('Reading file...')
    # Default raw data directory.
    path = './rawdata'
    try:
        f = open(os.path.join(path, filename), 'r', encoding='utf-8')
    except FileNotFoundError:
        print('File does not exist!')
        return False
    lines = f.readlines()
    f.close()
    return lines


def writefile(lines, location='../data/data_preprocessed.txt'):
    print('Writing file...')
    with open(location, 'w', encoding='utf-8') as f:
        try:
            for line in lines:
                f.write(line)
        except IOError:
            print('IOError! Write file failed.')
            return False
    print('Write file finished!')
    return True


def make_script_dict():
    print('Making script dict...')
    lines = readfile('script_medicine.txt')
    script_medicine = {}
    for line in lines:
        tokens = line.split(':')
        try:
            script_name = tokens[0]
            medicines = tokens[1].split(',')
        except IndexError:
            print('IndexError in line:')
            print(line)
            continue
        script_medicine[script_name] = medicines
    print('Script dict created.')
    return script_medicine


def preprocess():
    print('Start preprocessing...')
    symptom_script = readfile('symptom_script.txt')
    script_medicine = make_script_dict()
    symptoms = []
    lines = []
    for line in symptom_script:
        if not len(line):
            continue
        re_symptom = re.compile('\[(.+)\]')
        re_script = re.compile('【(.+)】')
        symptom = re_symptom.match(line)
        script = re_script.match(line)
        if symptom:
            # Cache symptom
            symptoms.append(symptom.group(1))
            continue
        if script:
            # For every symptom in symptoms, append script medicines.
            script_name = script.group(1)
            for symptom in symptoms:
                symptom_medicine = '{},{}'.format(symptom, ','.join(script_medicine[script_name]))
                lines.append(symptom_medicine)
            symptoms = []
    writefile(lines)
    print('Preprocessing finished.')

preprocess()