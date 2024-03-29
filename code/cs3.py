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
            factor = multipliers[occurrence_times[i + 1]
                                 ] / multipliers[occurrence_times[i]]
            if factor > 60:
                raise ValueError('Illegal occurrence times',
                                 occurrence_times[i], occurrence_times[i + 1])

            higher_unit_time = base_time + LOWER_RANGE
            lower_unit_time = round(higher_unit_time * factor)

            for premise_direction in ['forward', 'backward']:
                for hypothesis_direction in ['forward', 'backward']:
                    for premise_preposition in ['in', 'before', 'after']:
                        for lut in ['lower', 'higher']:
                            for hypo_preposition in ['before', 'after']:
                                # higher_unit_time_lower = random.randint(1, higher_unit_time - 1)
                                lower_unit_time_lower = random.randint(
                                    max(round(max(0, higher_unit_time - DIFF_RANGE) * factor), 1), lower_unit_time - 1)

                                # higher_unit_time_higher = random.randint(higher_unit_time + 1, UPPER_RANGE)
                                lower_unit_time_higher = random.randint(lower_unit_time + 1,
                                                                        round((higher_unit_time + DIFF_RANGE) * factor))
                                lower_unit_time_cur = lower_unit_time_lower if lut == 'lower' else lower_unit_time_higher

                                lower_higher_diff = (
                                    lower_unit_time_cur - (higher_unit_time * factor)) / factor

                                forward_premise = ' '.join(
                                    [forward_template, premise_preposition, str(higher_unit_time),
                                     get_occurrence_time_name(occurrence_times[i + 1],
                                                              higher_unit_time) + '.'])
                                backward_premise = ' '.join([premise_preposition.capitalize(), str(higher_unit_time),
                                                             get_occurrence_time_name(occurrence_times[i + 1],
                                                                                      higher_unit_time) + ',',
                                                             backward_template + '.'])
                                forward_hypothesis = ' '.join(
                                    [forward_template, hypo_preposition, str(lower_unit_time_cur),
                                     get_occurrence_time_name(occurrence_times[i],
                                                              lower_unit_time_cur) + '.'])
                                backward_hypothesis = ' '.join([hypo_preposition.capitalize(), str(lower_unit_time_cur),
                                                                get_occurrence_time_name(occurrence_times[i],
                                                                                         lower_unit_time_cur) + ',',
                                                                backward_template + '.'])

                                label = get_label(
                                    premise_preposition, lut, hypo_preposition)
                                dataset_list.append(
                                    [forward_premise if premise_direction == 'forward' else backward_premise,
                                     forward_hypothesis if hypothesis_direction == 'forward' else backward_hypothesis,
                                     label, premise_preposition, occurrence_times[i +
                                                                                  1], premise_direction,
                                     hypothesis_direction, lower_higher_diff])


def generate_samples_for_templates(templates_file, dataset_file_path):
    templates_df = pd.read_csv(templates_file)

    dev_inds = [20, 21, 22, 23, 24, 25, 40, 41,
                42, 43, 44, 45, 50, 53, 55, 61, 67, 69]
    train_templates_df = templates_df.iloc[[
        idx for idx in templates_df.index if idx not in dev_inds]]
    test_templates_df = templates_df.iloc[dev_inds]
    train_templates_df.reset_index(inplace=True, drop=True)
    test_templates_df.reset_index(inplace=True, drop=True)

    train_templates_df = train_templates_df[~pd.isna(
        train_templates_df['Forward Future Template'])]
    test_templates_df = test_templates_df[~pd.isna(
        test_templates_df['Forward Future Template'])]

    train_dataset_list = []
    test_dataset_list = []

    train_templates_df.apply(
        generate_samples_for_template, args=(train_dataset_list,), axis=1)
    test_templates_df.apply(generate_samples_for_template,
                            args=(test_dataset_list,), axis=1)

    train_dataset_df = pd.DataFrame(train_dataset_list,
                                    columns=['Premise', 'Hypothesis', 'Label', 'Premise Preposition',
                                             'Higher Duration Unit',
                                             'Premise Direction', 'Hypothesis Direction', 'Lower/Higher Diff'])
    train_dataset_df.to_csv(dataset_file_path + '/cs3_train.csv')

    test_dataset_df = pd.DataFrame(test_dataset_list,
                                   columns=['Premise', 'Hypothesis', 'Label', 'Premise Preposition',
                                            'Higher Duration Unit',
                                            'Premise Direction', 'Hypothesis Direction', 'Lower/Higher Diff'])
    test_dataset_df.to_csv(dataset_file_path + '/cs3_test.csv')

    print('Train Dataset Instances:', train_dataset_df.shape[0])

    print('Test Dataset Instances:', test_dataset_df.shape[0])


if __name__ == "__main__":
    generate_samples_for_templates('../data/templates.csv', '../data/')
