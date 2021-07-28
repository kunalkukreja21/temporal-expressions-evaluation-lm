import random
import pandas as pd
import numpy as np

multipliers = {
    'second': 1,
    'minutes': 60,
    'day_time': 3600,
    'day': 86400,
    'month': 2.628e+6,
    'year': 3.154e+7
}

"""
in 5 hours
    before 6 hours -> E
    before 4 hours -> C
    after 10 hours -> C
    after 3 hours -> E
before 5 hours
    before 3 hours -> N
    before 10 hours -> E
    after 3 hours -> N
    after 10 hours -> C
after 5 hours
    before 3 hours -> C
    before 10 hours -> N
    after 3 hours -> E
    after 10 hours -> N
"""

UPPER_RANGE = 11
LOWER_RANGE = 1
DIFF_RANGE = 5


def get_label(premise_preposition, lut, hypo_preposition):
    if premise_preposition == 'in':
        if hypo_preposition == 'before':
            return 'E' if lut == 'higher' else 'C'
        elif hypo_preposition == 'after':
            return 'E' if lut == 'lower' else 'C'
    elif premise_preposition == 'before':
        if hypo_preposition == 'before':
            return 'N' if lut == 'lower' else 'E'
        if hypo_preposition == 'after':
            return 'N' if lut == 'lower' else 'C'
    elif premise_preposition == 'after':
        if hypo_preposition == 'before':
            return 'C' if lut == 'lower' else 'N'
        if hypo_preposition == 'after':
            return 'E' if lut == 'lower' else 'N'
    raise ValueError('Unexpected value: ', premise_preposition)


def main():
    templates_df = pd.read_csv('../data/templates.csv')


def get_occurrence_time_name(occurrence_time_key, occurrence_time_value):
    return ('hour' if occurrence_time_key == 'day_time' else occurrence_time_key) + \
           ('s' if occurrence_time_value > 1 else '')


def generate_samples_for_template(template_df_row, dataset_list):
    forward_template, backward_template, occurrence = template_df_row['Forward Future Template'], \
                                                      template_df_row['Backward Future Template'], \
                                                      template_df_row['Occurrence Future']
    occurrence_times = occurrence.split(', ')

    for i in range(len(occurrence_times) - 1):
        for base_time in range(UPPER_RANGE - LOWER_RANGE):
            factor = multipliers[occurrence_times[i + 1]] / multipliers[occurrence_times[i]]
            if factor > 60:
                raise ValueError('Illegal occurrence times', occurrence_times[i], occurrence_times[i + 1])

            higher_unit_time = base_time + LOWER_RANGE
            lower_unit_time = round(higher_unit_time * factor)

            for premise_forward_backward in ['forward', 'backward']:
                for premise_preposition in ['in', 'before', 'after']:
                    for lut in ['lower', 'higher']:
                        for hypo_preposition in ['before', 'after']:
                            # higher_unit_time_lower = random.randint(1, higher_unit_time - 1)
                            lower_unit_time_lower = random.randint(
                                max(round(max(0, higher_unit_time - DIFF_RANGE) * factor), 1), lower_unit_time - 1)

                            # higher_unit_time_higher = random.randint(higher_unit_time + 1, UPPER_RANGE)
                            lower_unit_time_higher = random.randint(lower_unit_time + 1,
                                                                    round((higher_unit_time + DIFF_RANGE) * factor))

                            if premise_forward_backward == 'forward':
                                premise = ' '.join([forward_template, premise_preposition, str(higher_unit_time),
                                                    get_occurrence_time_name(occurrence_times[i + 1],
                                                                             higher_unit_time) + '.'])
                            elif premise_forward_backward == 'backward':
                                premise = ' '.join([premise_preposition.capitalize(), str(higher_unit_time),
                                                    get_occurrence_time_name(occurrence_times[i + 1],
                                                                             higher_unit_time) + ',',
                                                    backward_template + '.'])
                            lower_unit_time_cur = lower_unit_time_lower if lut == 'lower' else lower_unit_time_higher
                            hypo = ' '.join([forward_template, hypo_preposition, str(lower_unit_time_cur),
                                             get_occurrence_time_name(occurrence_times[i], lower_unit_time_cur) + '.'])
                            label = get_label(premise_preposition, lut, hypo_preposition)
                            dataset_list.append([premise, hypo, label, premise_preposition, occurrence_times[i + 1],
                                                 premise_forward_backward])


def generate_samples_for_templates(templates_file, dataset_file_path):
    templates_df = pd.read_csv(templates_file)
    templates_df = templates_df[~pd.isna(templates_df['Forward Future Template'])]

    msk = np.random.rand(len(templates_df)) < 0.8
    train_templates_df = templates_df[msk]
    test_templates_df = templates_df[~msk]

    train_dataset_list = []
    test_dataset_list = []

    train_templates_df.apply(generate_samples_for_template, args=(train_dataset_list,), axis=1)
    test_templates_df.apply(generate_samples_for_template, args=(test_dataset_list,), axis=1)

    train_dataset_df = pd.DataFrame(train_dataset_list,
                              columns=['Premise', 'Hypothesis', 'Label', 'Premise Preposition', 'Higher Duration Unit',
                                       'Premise Forward/Backward'])
    train_dataset_df.to_csv(dataset_file_path + '/cs3-train.csv')

    test_dataset_df = pd.DataFrame(test_dataset_list,
                                    columns=['Premise', 'Hypothesis', 'Label', 'Premise Preposition',
                                             'Higher Duration Unit',
                                             'Premise Forward/Backward'])
    test_dataset_df.to_csv(dataset_file_path + '/cs3-test.csv')


    print('Train dataset stats')
    print(train_dataset_df['Label'].value_counts())
    print(train_dataset_df['Premise Preposition'].value_counts())
    print(train_dataset_df['Higher Duration Unit'].value_counts())
    print(train_dataset_df['Premise Forward/Backward'].value_counts())

    print('Test dataset stats')
    print(test_dataset_df['Label'].value_counts())
    print(test_dataset_df['Premise Preposition'].value_counts())
    print(test_dataset_df['Higher Duration Unit'].value_counts())
    print(test_dataset_df['Premise Forward/Backward'].value_counts())


if __name__ == "__main__":
    generate_samples_for_templates('../data/templates.csv', '../data/')
