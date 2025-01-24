import datetime

def timedeltastr_to_sec(time_str: str):
    """
    
    datetime.timedelta (str) を秒 (float) に変換する
    
    """
    h, m, s = [float(i) for i in time_str.split(':')]
    return datetime.timedelta(hours=h, minutes=m, seconds=s).total_seconds()

def calc_ave_sec(timedelta_str_list: list[str]):
    """
    
    datetime.timedelta (str) からその平均（秒）を計算

    Examples:
        calc_ave_sec([
            "0:01:19.987043",
            "0:01:18.944787",
            "0:01:19.954586",
            "0:01:21.153599",
            "0:01:18.677560",
        ])
    
    """
    li = [timedeltastr_to_sec(i) for i in timedelta_str_list]
    return sum(li)/len(li)
