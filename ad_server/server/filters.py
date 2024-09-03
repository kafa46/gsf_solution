def format_datetime(value, date_format='%Y년 %m월 %d일 %H:%M'):
    return value.strftime(date_format)

def format_datetime_simple(value, date_format='%Y년 %m월 %d일'):
    return value.strftime(date_format)

def format_datetime_simple_with_dash(value, date_format='%y-%m-%d'):
    return value.strftime(date_format)

def format_datetime_for_input_calendar(value, date_format='%Y-%m-%d'):
    return value.strftime(date_format)

def format_datetime_for_abbreviated(value, date_format="'%y.%m.%d."):
    if value is None:
        return ''
    return value.strftime(date_format)

def format_datetime_year_only(value, date_format="%Y"):
    if value is None:
        return ''
    return value.strftime(date_format)

def make_short_string(sentence, max_len=20):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def make_short_string_7(sentence, max_len=7):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '..'

def make_short_string_10(sentence, max_len=11):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '..'

def make_short_string_gallery(sentence, max_len=13):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def make_short_string_home(sentence, max_len=17):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def make_short_string_70chars(sentence, max_len=67):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def make_short_string_30chars(sentence, max_len=27):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def make_short_string_10chars(sentence, max_len=7):
    if len(sentence) < max_len:
        return sentence
    else:
        return sentence[:max_len] + '...'

def year_filter(target_year:int, datetime_list):
    datetime_list_filtered = []
    for x in datetime_list:
        if int(x.update_date.year) == target_year:
            datetime_list_filtered.append(x)
    return datetime_list_filtered

def short_img_path(full_img_path):
    '''Make short image file name
    from stored full image path in DB
    '''
    return full_img_path.split('/')[-1].split('_')[-1].strip()

def get_num_of_lines(string_text):
    lines_splited_by_backslashN = string_text.split('\n')
    return len(lines_splited_by_backslashN) + 4

def none_filter(arg):
    return arg if arg else '자료 없음'

def get_num_attendance(attendance_index_list):
    return sum(attendance_index_list)

def url_trim(url_path):
    print(f'url_path: {url_path}, type: {type(url_path)}')
    url_path = str(url_path)
    if url_path.startswith('server'):
        return url_path.replace('server', '')

def comma_seperate(str_num) -> str:
    '''문자열로 된 숫자에 세자리 콤마찍기'''
    return format(str_num, ',')

def remove_phd_master(text) -> str:
    '''문자열로 된 숫자에 세자리 콤마찍기'''
    return text.replace('[박사학위 논문] ', '').replace('[석사학위 논문] ', '')