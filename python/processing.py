import csv
import copy


def parser(filename):

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        total_list = list(reader)
        coln = total_list[0]
        cold = dict(enumerate(coln))
        cold = {v: k for k, v in cold.items()}
        values = total_list[1:]
        print(cold, coln)

    return [cold, coln, values]


def is_valid_pair(i,w,l,col,values):
    if values[i][col['m']] != '':
        # it is a pair
        if i-w >= 0 and i+w < l:
            # list is not out of range
            if are_all_the_same(get_values(i, w, w,'temporada',col,values)):
                # the same season
                if are_all_the_same(get_values(i, w, w, 'time', col, values)):
                    # the same team
                    if values[i][col['trocou']] == '0':
                        if are_all_the_same(get_values(i, w, w-1, 'trocou', col, values)):
                            # if it did not change, should not change in the entire window
                            return True
                    else:
                        # if changed, does not matter if changed again
                        return True
    return False


def get_values(i,mw,pw,name,col,values):
    return [v[col[name]] for v in values[i-mw:i+pw+1]]


def are_all_the_same(iterator):
        return len(set(iterator)) <= 1


def write_csv(filename,coln, buffer):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows([coln])
        writer.writerows(buffer)


def remove_single(pairs):
    # finding singles
    single = []
    k = 0
    while k < len(pairs):
        if k == len(pairs)-1:
            # it is the last one
            single.append(k)
            k += 1
        else:
            # exists a later element
            if pairs[k][cold['m']] == pairs[k+1][cold['m']] and pairs[k][cold['time']] == pairs[k+1][cold['time']]:
                # double checking if trocou are different
                if pairs[k][cold['trocou']] == pairs[k + 1][cold['trocou']]:
                    print(w,k)
                    print(pairs[k])
                    print(pairs[k+1])
                    raise ValueError('The pair has the same value of trocou, the algorithm has to be improved.')
                # it is married pair
                k += 2
            else:
                single.append(k)
                k += 1

    # removing singles
    married_pairs = []
    for j in range(len(pairs)):
        if j not in single:
            married_pairs.append(pairs[j])

    return married_pairs


def getting_windowed_data(pairs):
    out = []
    for p in pairs:
        i = p[-1]
        for k in range(i-w,i+w+1):
            line = copy.deepcopy(values[k])
            # copying m to the entire window
            line[cold['m']] = values[i][cold['m']]
            # adding periodo
            if k < i :
                line[cold['periodo']] = 0
            elif k > i:
                line[cold['periodo']] = 1
            # copying m to the entire window
            line[cold['tratado']] = values[i][cold['trocou']]
            out.append(line)
    return out


# getting colunms and values
in_filename = '../data/base.csv'
[cold, coln, values] = parser('../data/base.csv')
l = len(values)

for w in range(1, 13):
    # getting valid pairs
    pairs = []
    for i in range(len(values)):
        if is_valid_pair(i,w,l,cold,values):
            pairs.append(values[i]+[i])

    # sorting by m and then by time
    pairs = sorted(pairs,key=lambda x: x[cold['m']])
    pairs = sorted(pairs,key=lambda x: x[cold['time']])

    # removing single pairs
    pairs = remove_single(pairs)

    # saving preliminary result for debug purposes
    write_csv('{name:s}_pairs_window_{w:03d}.csv'.format(name=in_filename.split('.csv')[0],w=w), coln, pairs)

    # getting windowed data
    out = getting_windowed_data(pairs)

    # writing windowed data
    write_csv('{name:s}_window_{w:03d}.csv'.format(name=in_filename.split('.csv')[0],w=w), coln, out)


