import pandas as pd
import requests
import os

# scroll down to the bottom to implement your solution

if __name__ == '__main__':

    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if ('A_office_data.xml' not in os.listdir('../Data') and
        'B_office_data.xml' not in os.listdir('../Data') and
        'hr_data.xml' not in os.listdir('../Data')):
        print('A_office_data loading.')
        url = "https://www.dropbox.com/s/jpeknyzx57c4jb2/A_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/A_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('B_office_data loading.')
        url = "https://www.dropbox.com/s/hea0tbhir64u9t5/B_office_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/B_office_data.xml', 'wb').write(r.content)
        print('Loaded.')

        print('hr_data loading.')
        url = "https://www.dropbox.com/s/u6jzqqg1byajy0s/hr_data.xml?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/hr_data.xml', 'wb').write(r.content)
        print('Loaded.')

        # All data in now loaded to the Data folder.

    data_A = pd.read_xml('../Data/A_office_data.xml')
    #  print(data_A.shape)
    #  print(data_A.axes)
    #  print(data_A.info())
    data_A['new_index'] = ["A"+id_ for id_ in data_A["employee_office_id"].map(str)]
    data_A.set_index('new_index', inplace=True)
    #  print(data_A.index.tolist())
    data_B = pd.read_xml('../Data/B_office_data.xml')
    #  print(data_B.info())
    #  print(data_B.axes)
    #  print(data_B.info())
    data_B['new_index'] = ["B" + id_ for id_ in data_B["employee_office_id"].map(str)]
    data_B.set_index('new_index', inplace=True)
    #  print(data_B.index.tolist())
    data_hr = pd.read_xml('../Data/hr_data.xml')
    #  print(data_hr.info())
    #  print(data_hr.axes)
    #  print(data_hr.info())
    data_hr.set_index('employee_id', inplace=True)
    #  print(data_hr.index.tolist())

    df = pd.concat([data_A, data_B])
    df = df.merge(data_hr, how="left",
                  left_index=True, right_index=True,
                  indicator=True)
    df = df[(df._merge == 'both')]
    df = df.drop(['employee_office_id', '_merge'], axis=1)
    df = df.sort_index()

    #  What are the departments of the top ten employees in terms of working hours?
    #  Output a Python list of values;
    #  print(df.sort_values('average_monthly_hours',ascending=False).Department.head(10).tolist())
    #  What is the total number of projects on which IT department employees
    #  with low salaries have worked? Output a number;
    #  print(df[(df.Department == "IT") & (df.salary == "low")].number_project.sum())
    #  What are the last evaluation scores and the satisfaction levels of the
    #  employees A4, B7064, and A3033? Output a Python list where each entry is
    #  a list of values of the last evaluation score and the satisfaction level
    #  of an employee. The data for each employee should be specified in the same
    #  order as the employees' IDs in the question above.
    #  Apply the .loc method of pandas to answer the question!
    desired_employees = ['A4', 'B7064', 'A3033']
    subdf = df.loc[desired_employees, ['last_evaluation', 'satisfaction_level']]
    #  print([row.tolist() for i, row in subdf.iterrows()])

    # Stage 4/5
    def count_bigger_5(series):
        return series[series > 5].count()

    #  print(df.groupby('left').agg({'number_project': ['median', count_bigger_5],
    #                              'time_spend_company': ['mean', 'median'],
    #                              'Work_accident': 'mean',
    #                              'last_evaluation': ['mean', 'std']}).round(2).to_dict())


    # Stage 5/5 Pivot tables
    # The first pivot table is a table that displays departments as rows and the employee's current status
    # (the left column) and their salary level (the salary column) as columns.
    # The values should be the median number of hours employees have worked per month
    # (the average_monthly_hours columns). In the table, the HR boss wants to see only those departments where either one is true:
    #      -  For the currently employed: the median value of the working hours of high-salary employees is
    #         smaller than the hours of the medium-salary employees, OR:
    #      -  For the employees who left: the median value of working hours of low-salary employees
    #         is smaller than the hours of high-salary employees
    pivot_median_hours = df.pivot_table(index='Department',
                                        columns=['left', 'salary'],
                                        values='average_monthly_hours', aggfunc='median')
    condition = (pivot_median_hours[(0.0,   'high')] < pivot_median_hours[(0.0,   'medium')]) \
                | (pivot_median_hours[(1.0,   'low')] < pivot_median_hours[(1.0,   'high')])

    print(pivot_median_hours[condition].round(2).to_dict())

    #  The second pivot table is a table where each row is an employee's time in the company (time_spend_company);
    #  the columns indicate whether an employee has had any promotion (the promotion_last_5years column). The values
    #  are min, max, the mean of the last evaluation score and the satisfaction level (the satisfaction_level
    #  and last_evaluation columns). Filter the table by the following rule: select only those rows where
    #  the last mean evaluation score is higher for those who didn't have any promotion than those who had.
    pivot_satisfaction = df.pivot_table(index='time_spend_company',
                                        columns='promotion_last_5years',
                                        values=['satisfaction_level', 'last_evaluation'],
                                        aggfunc=['min', 'max', 'mean'])
    condition = pivot_satisfaction[('mean', 'last_evaluation', 0)] > pivot_satisfaction[('mean', 'last_evaluation', 1)]
    print(pivot_satisfaction[condition].round(2).to_dict())
