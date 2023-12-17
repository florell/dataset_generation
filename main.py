import csv

import pandas
import random
from datetime import datetime, timedelta
from numpy import random as nprandom
from styleframe import StyleFrame

columns = {"ФИО": [], "Паспортные данные": [], "Откуда": [], "Куда": [], "Дата отъезда": [], "Дата приезда": [],
           "Рейс": [], "Вагон и место": [],
           "Стоимость": [],
           "Карта оплаты": [],
           "Банк": []
           }
######################################
surnames_male = []
surnames_female = []
pat_m = []
pat_f = []
cities = []
male_names = set()
female_names = set()
races = dict()
seasonal = {'summer': [], 'autumn': [], 'winter': [], 'spring': []}


def rand_snp():
    gender = random.randint(0, 1)
    return ' '.join((surnames_female[random.randrange(0, len(surnames_female))],
                     female_names[random.randrange(0, len(female_names))],
                     pat_f[random.randrange(0, len(pat_f))]) if gender == 0 else
                    (surnames_male[random.randrange(0, len(surnames_male))],
                     male_names[random.randrange(0, len(male_names))],
                     pat_m[random.randrange(0, len(pat_m))]))


def rand_passport():
    flag = random.randint(0, 1)
    region = str(random.randint(1, 99))
    if len(region) == 1: region = '0' + region
    year = str(random.randint(53, 99)) if flag else str(random.randint(1, 23))
    if len(year) == 1: year = '0' + year
    return ' '.join((region + year, str(random.randint(100000, 999999))))


def fromto():
    pair = 0
    from_ = cities[random.randrange(0, len(cities))]
    to = cities[random.randrange(0, len(cities))]
    while from_ == to:
        to = cities[random.randrange(0, len(cities))]
    pair = (from_, to)
    return pair


def generate_card(bank_probabilities, net_probabilities):
    bank_list = ["Сбербанк", "Тинькофф", "Альфабанк", "Райффайзен", "ВТБ"]
    net_list = [("Visa", 4), ("Mastercard", 5), ("Maestro", 3), ("МИР", 2)]
    # print(bank_list, bank_probabilities, len(bank_list), len(bank_probabilities))
    bank = nprandom.choice(bank_list, size=1, p=bank_probabilities)[0]
    # print(net_probabilities, net_list)
    net_index = nprandom.choice(range(len(net_list)), size=1, p=net_probabilities)[0]
    net_name, first_num = net_list[net_index]

    card = random.randint(0, 999)

    if card < 10:
        card = str(first_num) + '00' + str(card)
    elif 10 <= card < 100:
        card = str(first_num) + '0' + str(card)
    else:
        card = str(first_num) + str(card)
    for _ in range(3):
        temp = random.randint(0, 9999)
        if temp < 10:
            temp = '000' + str(temp)
        elif 10 <= temp < 100:
            temp = '00' + str(temp)
        elif 100 <= temp < 1000:
            temp = '0' + str(temp)
        card += ' ' + str(temp)

    return (card, bank)


with open("surnames.csv") as s_raw, open("male_names.csv") as m_raw, open("female_names.csv") as f_raw, \
        open("slavic-female-patronymics.txt") as pf_raw, open("slavic-male-patronymics.txt") as pm_raw, \
        open('cities.txt') as c_raw:
    data_s = csv.reader(s_raw)
    data_mn = csv.reader(m_raw)
    data_fn = csv.reader(f_raw)
    data_pf = pf_raw.read().split('\n')
    data_pm = pm_raw.read().split('\n')
    data_cities = c_raw.read().split('\n')

    for string in data_s:
        surnames_male.append(string[1].capitalize())
        surnames_female.append(string[1].capitalize() + 'а')
    for string in data_mn:
        male_names.add(string[1])
    male_names = list(male_names)
    for string in data_fn:
        female_names.add(string[1])
    female_names = list(female_names)

    pat_m = data_pm
    pat_f = data_pf
    cities = data_cities


class Train:
    def __init__(self, race, c_amount, departure_date, arrival_date, from_, to):
        self.race = race
        self.c_amount = c_amount
        self.carriges = []
        self.departure_date = departure_date
        self.arrival_date = arrival_date
        self.from_ = from_
        self.to = to

    def create_train(self, banks_probs, net_probs):
        for c in range(self.c_amount):
            if 1 <= self.race <= 598:
                possible_types = [('3Э', 1.1, 25), ('2Э', 1.55, 20), ('1Б', 1.4, 20), ('1Л', 1.7, 24), ('1А', 2.2, 16),
                                  ('1И', 2.1, 16)]
            elif 701 <= self.race <= 750:
                possible_types = [('1С', 0.6, 40), ('1P', 1.5, 20), ('1В', 12.5, 1), ('2Р', 1.3, 35), ('2Е', 0.6, 40)]
            elif 751 <= self.race <= 788:
                flip = random.randint(0, 1)
                if flip:
                    possible_types = [('1Р', 2.1, 4), ('1В', 1.7, 30), ('1С', 1.5, 30), ('2С', 1.3, 35),
                                      ('2В', 1.4, 30), ('2Е', 1.5, 20)]
                else:
                    possible_types = [('1Е', 2.4, 2), ('1Р', 1.6, 30), ('2С', 1.2, 30)]
            else:
                possible_types = [None]
            pick = possible_types[random.randrange(len(possible_types))]
            temp = Carrige(c + 1, pick[0], pick[2], pick[1])
            temp.create_seats(banks_probs, net_probs)
            self.carriges.append(temp)

    def refill(self, banks_probs, net_probs):
        for c in self.carriges:
            c.clear_seats()
            c.create_seats(banks_probs, net_probs)


class Carrige():
    def __init__(self, c_number, c_type, s_amount, p_coeff):
        self.c_number = c_number
        self.c_type = c_type
        self.p_coeff = p_coeff
        self.s_amount = s_amount
        self.seats = []

    def create_seats(self, banks_probs, net_probs):
        for s in range(self.s_amount):
            cs = fromto()
            g_card = generate_card(bank_probabilities=banks_probs, net_probabilities=net_probs)
            passanger = [rand_snp(), rand_passport(), cs[0], cs[1],
                         g_card[0], g_card[1]]
            temp_s = Seat(s + 1, random.randint(1000, 3000) * self.p_coeff, passanger)
            self.seats.append(temp_s)

    def clear_seats(self):
        self.seats = []


class Seat:
    def __init__(self, number, price, taken_by):
        self.number = number
        self.price = price
        self.taken_by = taken_by


def generate(strings_amount, banks_list, ps_list):
    cur_amount = 0
    while cur_amount < strings_amount:
        race = random.choice((random.randrange(1, 298, 2), random.randrange(301, 598, 2), random.randrange(701, 788, 2)))
        c_amount = random.randrange(10, 26, 5)
        departure_date = None
        arrival_date = None
        month = None
        if race not in races.keys():
            if 151 <= race <= 298 or 451 <= race <= 598:
                if race in seasonal.values():
                    if race in seasonal['winter']:
                        month = random.choice([1, 2, 12])
                    elif race in seasonal['spring']:
                        month = random.randint(3, 5)
                    elif race in seasonal['summer']:
                        month = random.randint(6, 8)
                    elif race in seasonal['autumn']:
                        month = random.randint(9, 11)
                else:
                    month = random.randint(1, 12)
                    if month == 1 or month == 2 or month == 12:
                        seasonal['winter'].append(race)
                        seasonal['winter'].append(race + 1)
                    elif month == 3 or month == 4 or month == 5:
                        seasonal['spring'].append(race)
                        seasonal['spring'].append(race + 1)
                    elif month == 6 or month == 7 or month == 8:
                        seasonal['summer'].append(race)
                        seasonal['spring'].append(race + 1)
                    elif month == 9 or month == 10 or month == 11:
                        seasonal['autumn'].append(race)
                        seasonal['spring'].append(race + 1) 
                departure_date = datetime(year=2023, month=month, day=random.randint(1, 28), hour=random.randint(0, 23),
                                          minute=random.randint(0, 59))
                if 151 <= race <= 298:
                    arrival_date = departure_date + timedelta(days=random.randint(2, 6),
                                                              hours=random.randint(1, 12),
                                                              minutes=random.randint(1, 59))
                else:
                    arrival_date = departure_date + timedelta(days=random.randint(5, 11),
                                                              hours=random.randint(1, 12),
                                                              minutes=random.randint(1, 59))
            elif 1 <= race <= 150 or 301 <= race <= 450:
                month = random.randint(1, 12)
                departure_date = datetime(year=2023, month=month, day=random.randint(1, 28), hour=random.randint(0, 23),
                                          minute=random.randint(0, 59))
                if 1 <= race <= 150:
                    arrival_date = departure_date + timedelta(days=random.randint(2, 6),
                                                              hours=random.randint(1, 12),
                                                              minutes=random.randint(1, 59))
                else:
                    arrival_date = departure_date + timedelta(days=random.randint(5, 11),
                                                              hours=random.randint(1, 12),
                                                              minutes=random.randint(1, 59))
            elif 701 <= race <= 750 or 751 <= race <= 788:
                month = random.randint(1, 12)
                departure_date = datetime(year=2023, month=month, day=random.randint(1, 28), hour=random.randint(0, 23),
                                          minute=random.randint(0, 59))
                if 701 <= race <= 750:
                    arrival_date = departure_date + timedelta(hours=random.randint(4, 8),
                                                              minutes=random.randint(0, 59))
                else:
                    arrival_date = departure_date + timedelta(hours=random.randint(2, 5),
                                                              minutes=random.randint(0, 59))
            from_, to = fromto()
            t = Train(race, c_amount, departure_date, arrival_date, from_, to)
            t.create_train(banks_list, ps_list)
            races[race] = (t, False)
        elif not races[race][1]:
            t = races[race][0]
            races[race] = ([t.departure_date], True)
            delta = t.arrival_date - t.departure_date
            t.refill(banks_list, ps_list)
            t.race += 1
            t.from_, t.to = t.to, t.from_
            t.departure_date = t.arrival_date + timedelta(hours=random.randint(6, 12))
            t.arrival_date = t.departure_date + delta
            races[race][0].append(t.arrival_date)
        else:
            flip = random.randint(0, 1)
            delta = races[race][0][1] - races[race][0][0] + timedelta(hours=random.randint(6, 12))
            if race not in seasonal.values():
                if flip:
                    departure_date = races[race][0][0] - delta
                    arrival_date = races[race][0][1] - delta
                    while races[race][0][0] < arrival_date < races[race][0][1]:
                        departure_date = races[race][0][0] - delta
                        arrival_date = races[race][0][1] - delta
                else:
                    departure_date = races[race][0][0] + delta
                    arrival_date = races[race][0][1] + delta
                    while races[race][0][0] < departure_date < races[race][0][1]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
            else:
                if race in seasonal['winter']:
                    if (races[race][0][0] - delta).month not in [1, 2, 12]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < departure_date < races[race][0][1]:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                    elif (races[race][0][1] + delta).month not in [1, 2, 12]:
                        departure_date = races[race][0][0] - delta
                        arrival_date = races[race][0][1] - delta
                        while races[race][0][0] < arrival_date < races[race][0][1]:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                    else:
                        if flip:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                            while races[race][0][0] < arrival_date < races[race][0][1]:
                                departure_date = races[race][0][0] - delta
                                arrival_date = races[race][0][1] - delta
                        else:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                            while races[race][0][0] < departure_date < races[race][0][1]:
                                departure_date = races[race][0][0] + delta
                                arrival_date = races[race][0][1] + delta

                elif race in seasonal['spring']:
                    if (races[race][0][0] - delta).month not in [3, 4, 5]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < departure_date < races[race][0][1]:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                    elif (races[race][0][1] + delta).month not in [3, 4, 5]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < arrival_date < races[race][0][1]:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                    else:
                        if flip:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                            while races[race][0][0] < departure_date < races[race][0][1]:
                                departure_date = races[race][0][0] + delta
                                arrival_date = races[race][0][1] + delta
                            while races[race][0][0] < arrival_date < races[race][0][1]:
                                departure_date = races[race][0][0] - delta
                                arrival_date = races[race][0][1] - delta
                        else:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                            while races[race][0][0] < departure_date < races[race][0][1]:
                                departure_date = races[race][0][0] + delta
                                arrival_date = races[race][0][1] + delta

                elif race in seasonal['summer']:
                    if (races[race][0][0] - delta).month not in [6, 7, 8]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < departure_date < races[race][0][1]:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                    elif (races[race][0][1] + delta).month not in [6, 7, 8]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < arrival_date < races[race][0][1]:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                    else:
                        if flip:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                            while races[race][0][0] < arrival_date < races[race][0][1]:
                                departure_date = races[race][0][0] - delta
                                arrival_date = races[race][0][1] - delta
                        else:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                            while races[race][0][0] < departure_date < races[race][0][1]:
                                departure_date = races[race][0][0] + delta
                                arrival_date = races[race][0][1] + delta
                elif race in seasonal['autumn']:
                    if (races[race][0][0] - delta).month not in [9, 10, 11]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < departure_date < races[race][0][1]:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                    elif (races[race][0][1] + delta).month not in [9, 10, 11]:
                        departure_date = races[race][0][0] + delta
                        arrival_date = races[race][0][1] + delta
                        while races[race][0][0] < arrival_date < races[race][0][1]:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                        if flip:
                            departure_date = races[race][0][0] - delta
                            arrival_date = races[race][0][1] - delta
                            while races[race][0][0] < arrival_date < races[race][0][1]:
                                departure_date = races[race][0][0] - delta
                                arrival_date = races[race][0][1] - delta
                        else:
                            departure_date = races[race][0][0] + delta
                            arrival_date = races[race][0][1] + delta
                            while races[race][0][0] < departure_date < races[race][0][1]:
                                departure_date = races[race][0][0] + delta
                                arrival_date = races[race][0][1] + delta
            from_, to = fromto()
            t = Train(race, c_amount, departure_date, arrival_date, from_, to)
            t.create_train(banks_list, ps_list)
            races[race] = (t, False)

        for car in t.carriges:
            for s in car.seats:
                if cur_amount > strings_amount: break
                columns['ФИО'].append(s.taken_by[0])
                columns['Паспортные данные'].append(s.taken_by[1])
                columns['Откуда'].append(t.from_)
                columns['Куда'].append(t.to)
                # print(t.departure_date, race)
                # print(t.arrival_date)
                try:
                    columns['Дата отъезда'].append(t.departure_date.strftime('%Y-%m-%dT%H:%M'))
                    columns['Дата приезда'].append(t.arrival_date.strftime('%Y-%m-%dT%H:%M'))
                except:
                    columns['Дата отъезда'].append('fucked up')
                    columns['Дата приезда'].append('fucked up')
                
                columns['Рейс'].append(t.race)
                columns['Вагон и место'].append(str(car.c_number) + '-' + str(s.number))
                columns['Стоимость'].append(s.price)
                columns['Карта оплаты'].append(s.taken_by[4])
                columns['Банк'].append(s.taken_by[5])
                cur_amount += 1
        if cur_amount > strings_amount: break
    df = pandas.DataFrame.from_dict(columns)
    # df = df.sample(frac=1)
    print(df)
# todo: сменить StyleFrame на DataFrame и поставить другой движок (медленно пиздец)
    # excel_writer = StyleFrame.ExcelWriter('output.xlsx')
    # sf = StyleFrame(df)
    # sf.to_excel(excel_writer, sheet_name='DataBase', best_fit=list(columns.keys()))
    # # excel_writer.save()

    writer = pandas.ExcelWriter('output.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='DataBase')
    writer.save()
    