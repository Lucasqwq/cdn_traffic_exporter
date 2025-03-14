# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import List


class DomainList(TeaModel):
    def __init__(
        self,
        domain_name: List[str] = None,
    ):
        # {"en":"Domain", "zh_CN":"域名"}
        self.domain_name = domain_name

    def validate(self):
        self.validate_required(self.domain_name, 'domain_name')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.domain_name is not None:
            result['domain-name'] = self.domain_name
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('domain-name') is not None:
            self.domain_name = m.get('domain-name')
        return self


class QueryDomainTotalTrafficRequest(TeaModel):
    def __init__(
        self,
        domain_list: DomainList = None,
    ):
        # {"en":"Domain list.
        #   Domain number limits can be adjusted depending on different accounts. The default value is 20(if you want to adjust,please, contact technical support)", "zh_CN":"域名列表
        #   1.域名个数限制根据账号可调,默认为20个(可联系技术支持下单调整);"}
        self.domain_list = domain_list

    def validate(self):
        self.validate_required(self.domain_list, 'domain_list')
        if self.domain_list:
            self.domain_list.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.domain_list is not None:
            result['domain-list'] = self.domain_list.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('domain-list') is not None:
            temp_model = DomainList()
            self.domain_list = temp_model.from_map(m['domain-list'])
        return self


class QueryDomainTotalTrafficResponseFlowData(TeaModel):
    def __init__(
        self,
        timestamp: str = None,
        flow: int = None,
    ):
        # {"en":"Date
        #   1.When the data query granularity is fiveminutes, the format is yyyy-MM-dd HH:mm; the data value of every time slice represents the data value within the previous time granularity range. The first time slice of the day is yyyy-MM-dd 00:05 AM, and the last one is yyyy-MM-dd 24:00.
        #   2.When the data query granularity is hourly, the format is yyyy-MM-dd HH; the data value of every time slice represents the data value within the previous time granularity range. The first time slice of the day is yyyy-MM-dd 00:01, and the last one is yyyy-MM-dd 24.
        #   3.When the data query granularity is daily, the format is yyyy-MM-dd; the data value of every time slice represents the value of the daily data.Return the time slice contained in start time and the time slice contained in end time", "zh_CN":"时间
        #   1.查询的数据粒度为fiveminutes时,格式为yyyy-MM-dd HH:mm;每一个时间片数据值代表的是前一个时间粒度范围内的数据值。一天开始的时间片是yyyy-MM-dd 00:05,最后一个时间片是yyyy-MM-dd 24:00。
        #   2.查询的数据粒度为hourly时,格式为yyyy-MM-dd HH;每一个时间片数据值代表的是前一个时间粒度范围内的数据值。一天开始的时间片是yyyy-MM-dd 01,最后一个时间片是yyyy-MM-dd 24。
        #   3.查询的数据粒度为daily时,格式为yyyy-MM-dd;每一个时间片数据值代表的该天内的数据值。
        #   4.返回开始时间和结束时间包含的时间片。"}
        self.timestamp = timestamp
        # {"en":"Traffic. Keep two digits of decimals. Unit: MB", "zh_CN":"流量,保留2位小数,单位为MB"}
        self.flow = flow

    def validate(self):
        self.validate_required(self.timestamp, 'timestamp')
        self.validate_required(self.flow, 'flow')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.timestamp is not None:
            result['timestamp'] = self.timestamp
        if self.flow is not None:
            result['flow'] = self.flow
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('timestamp') is not None:
            self.timestamp = m.get('timestamp')
        if m.get('flow') is not None:
            self.flow = m.get('flow')
        return self


class QueryDomainTotalTrafficResponse(TeaModel):
    def __init__(
        self,
        flow_summary: int = None,
        flow_data: List[QueryDomainTotalTrafficResponseFlowData] = None,
    ):
        # {"en":"Total traffic. Keep two digits of decimals. Unit: MB", "zh_CN":"总流量,保留2位小数,单位为MB"}
        self.flow_summary = flow_summary
        # {"en":"flowData", "zh_CN":"流量数据"}
        self.flow_data = flow_data

    def validate(self):
        self.validate_required(self.flow_summary, 'flow_summary')
        self.validate_required(self.flow_data, 'flow_data')
        if self.flow_data:
            for k in self.flow_data:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.flow_summary is not None:
            result['flow-summary'] = self.flow_summary
        if self.flow_data is not None:
            result['flow-data'] = []
            for k in self.flow_data:
                result['flow-data'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('flow-summary') is not None:
            self.flow_summary = m.get('flow-summary')
        if m.get('flow-data') is not None:
            self.flow_data = []
            for k in m.get('flow-data'):
                temp_model = QueryDomainTotalTrafficResponseFlowData()
                self.flow_data.append(temp_model.from_map(k))
        return self


class Paths(TeaModel):
    def __init__(self):
        pass

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        return self


class Parameters(TeaModel):
    def __init__(
        self,
        date_from: str = None,
        date_to: str = None,
        type: str = None,
    ):
        # {"en":"Start time
        # 1.The format is yyyy-MM-ddTHH:mm:ss+08:00;
        # 2.And smaller than the current time and 'dateTo';
        # 3.Period between 'dataFrom' and 'dateTo' cannot be longer than 31 days", "zh_CN":"开始时间
        # 1.格式为yyyy-MM-ddTHH:mm:ss+08:00;
        # 2.并且小于当前时间和dateTo;
        # 3.dateFrom和dateTo相差不能超过31天;4.只能查询最近2年内数据。"}
        self.date_from = date_from
        # {"en":"End time
        # 1.The format is yyyy-MM-ddTHH:mm:ss+08:00;
        # 2.Must be greater than 'dateFrom';
        # 3.If it's greater than the current time, then the current time is assigned as the value", "zh_CN":"结束时间
        # 1.格式为yyyy-MM-ddTHH:mm:ss+08:00;
        # 2.必须大于dateFrom;
        # 3.如果大于当前时间,则重新赋值为当前时间;"}
        self.date_to = date_to
        # {"en":"Data granularity
        # 1.fiveminutes: five minutes, hourly: one hour, daily: one day;
        # 2.If not specified, daily is set as the default value;
        # 3.If fiveminutes is specified as the value, then data is returned in actual configured granularity when there is specific configuration to data collecting granularity for the customer.", "zh_CN":"数据粒度
        # 1.fiveminutes:5分钟,hourly:1小时,daily:1天;
        # 2.不传递,默认为daily;
        # 3.传递fiveminutes时,若客户数据采集粒度有特殊配置将按实际配置粒度返回。"}
        self.type = type

    def validate(self):
        self.validate_required(self.date_from, 'date_from')
        self.validate_required(self.date_to, 'date_to')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.date_from is not None:
            result['dateFrom'] = self.date_from
        if self.date_to is not None:
            result['dateTo'] = self.date_to
        if self.type is not None:
            result['type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('dateFrom') is not None:
            self.date_from = m.get('dateFrom')
        if m.get('dateTo') is not None:
            self.date_to = m.get('dateTo')
        if m.get('type') is not None:
            self.type = m.get('type')
        return self


class RequestHeader(TeaModel):
    def __init__(self):
        pass

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        return self


class ResponseHeader(TeaModel):
    def __init__(self):
        pass

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        return self


