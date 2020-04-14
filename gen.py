import os
import sys
import calendar
import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# 休市日历列表(每次生成一年)
# todo 根据实际年份和情况修改此表
# 休市参考地址: http://www.sse.com.cn/disclosure/dealinstruc/closed/
CLOSE_DATE_LIST = [
    '2020-01-01',  # 元旦
    '2020-01-24', '2020-01-25', '2020-01-26', '2020-01-27', '2020-01-28', '2020-01-29', '2020-01-30', '2020-01-31', '2020-02-01', '2020-02-02',  # 春节
    '2020-04-04', '2020-04-05', '2020-04-06',  # 清明
    '2020-05-01', '2020-05-02', '2020-05-03', '2020-05-04', '2020-05-05',  # 劳动节
    '2020-06-25', '2020-06-26', '2020-06-27',  # 端午节
    '2020-09-22', '2020-09-23', '2020-09-24',  # 中秋
    '2020-10-01', '2020-10-02', '2020-10-03', '2020-10-04', '2020-10-05', '2020-10-06', '2020-10-07', '2020-10-08',  # 国庆
]


class SCDateNode:
    def __init__(self, date):
        # calendarDate, isOpen, prevTradeDate, isWeekEnd, isMonthEnd, isQuarterEnd, isYearEnd
        self.__date = date
        self.__date_str = date.strftime("%Y-%m-%d")
        self.__is_open = True           # 是否是交易日
        self.__prev_trade_date = ""     # 前一个交易日
        self.__is_week_end = False      # 每周最后一个交易日
        self.__is_month_end = False     # 每月最后一个交易日
        self.__is_quarter_end = False   # 每季最后一个交易日
        self.__is_year_end = False      # 每年最后一个交易日

    def date_str(self):
        return self.__date_str

    def date(self):
        return self.__date

    def set_prev_trade_date(self, _prev_trade_date):
        self.__prev_trade_date = _prev_trade_date

    def is_open(self):
        return self.__is_open

    def set_is_open(self, _is_open):
        self.__is_open = _is_open

    def set_is_week_end(self, _is_end):
        self.__is_week_end = _is_end

    def set_is_month_end(self, _is_end):
        self.__is_month_end = _is_end

    def set_is_quarter_end(self, _is_end):
        self.__is_quarter_end = _is_end

    def set_is_year_end(self, _is_end):
        self.__is_year_end = _is_end

    def __lt__(self, other):
        return self.__date < other.__date

    def __repr__(self):
        return '%s,%d,%s,%d,%d,%d,%d\n' % (self.__date_str.replace('-', ''), self.__is_open,
                                           self.__prev_trade_date.replace('-', ''), self.__is_week_end,
                                           self.__is_month_end, self.__is_quarter_end, self.__is_year_end)


class SCalendar:
    def __init__(self):
        # __date_list = map['yyyy-mm-dd'] = SCDateNode instance
        self.__date_list = {}
        self.__last_trade_date = ''

    def add_date_node(self, _node: SCDateNode):
        """
        添加日历节点
        :param _node: SCDateNode instance
        :return:
        """
        _node.set_prev_trade_date(self.__last_trade_date)

        if _node.is_open():
            self.__last_trade_date = _node.date_str()

            if self.__is_week_last_day(_node.date()):
                _node.set_is_week_end(True)

            if self.__is_month_last_day(_node.date()):
                _node.set_is_month_end(True)

            if self.__is_quarter_last_day(_node.date()):
                _node.set_is_quarter_end(True)

            if self.__is_year_last_day(_node.date()):
                _node.set_is_year_end(True)
        else:
            if len(self.__last_trade_date) > 0:
                last_trade_node = self.__date_list[self.__last_trade_date]

                if self.__is_week_last_day(_node.date()):
                    last_trade_node.set_is_week_end(True)

                if self.__is_month_last_day(_node.date()):
                    last_trade_node.set_is_month_end(True)

                if self.__is_quarter_last_day(_node.date()):
                    last_trade_node.set_is_quarter_end(True)

                if self.__is_year_last_day(_node.date()):
                    last_trade_node.set_is_year_end(True)

        # 加入节点
        self.__date_list[_node.date_str()] = _node

    @staticmethod
    def __is_week_last_day(_date):
        """
        判断指定日期是否是某周的最后一天
        :return:
        """
        return True if 6 == _date.weekday() else False

    @staticmethod
    def __is_month_last_day(_date):
        """
        判断指定日期是否是某月的最后一个交易日
        :return:
        """
        # 获取当月第一天的星期和当月的总天数
        _, month_range = calendar.monthrange(_date.year, _date.month)

        return True if _date.day == month_range else False

    @staticmethod
    def __is_quarter_last_day(_date):
        """
        判断指定日期是否是某季度的最后一个交易日
        :return:
        """
        if _date.strftime("%Y-%m-%d") in ['%d-03-31' % _date.year, '%d-06-30' % _date.year,
                                          '%d-09-30' % _date.year, '%d-12-31' % _date.year]:
            return True
        return False

    @staticmethod
    def __is_year_last_day(_date):
        """
        判断指定日期是否是某年的最后一个交易日
        :return:
        """
        if _date.strftime("%Y-%m-%d") in ['%d-12-31' % _date.year]:
            return True

        return False

    def __repr__(self):
        result = ["calendarDate,isOpen,prevTradeDate,isWeekEnd,isMonthEnd,isQuarterEnd,isYearEnd\n"]

        _keys = sorted(self.__date_list, key=self.__date_list.__getitem__)

        for key in _keys:
            result.append(str(self.__date_list[key]))

        return ''.join(result)


def enum_years(year):
    """
    遍历某一年的所有日期
    :param int year: 年份
    :return:
    """
    _calendar = SCalendar()
    delta = datetime.timedelta(days=1)
    begin = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    _date = begin
    while _date <= end:
        # 是否是周六日
        is_weekend = True if 5 <= _date.weekday() else False
        # 是否是节假日
        is_holiday = _date.strftime("%Y-%m-%d") in CLOSE_DATE_LIST

        _date_node = SCDateNode(_date)
        _date_node.set_is_open(not(is_weekend or is_holiday))

        _calendar.add_date_node(_date_node)
        
        _date += delta

    return _calendar

if __name__ == '__main__':
    target = datetime.datetime.strptime(CLOSE_DATE_LIST[0], "%Y-%m-%d")
    print(enum_years(target.year))
