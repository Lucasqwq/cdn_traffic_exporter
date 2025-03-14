import json
from auth.AkSkAuth import AkSkAuth
from model.AkSkConfig import AkSkConfig
from api.models.models import *


class Client:
    @staticmethod
    def main():
        queryDomainTotalTrafficRequest = QueryDomainTotalTrafficRequest()
        domainList = DomainList()
        domainList.domain_name = ["apt.yjxyjt.com","apt.x15022.com","apt.gggccb.com"]
        queryDomainTotalTrafficRequest.domain_list = domainList

        aksk_config = AkSkConfig()
        aksk_config.access_key = "qHr3LM0xWxv5iZhj7Fld0EggGvTVHGTWjEQi"
        aksk_config.secret_key = "ybRbueVBsiVjNfLYKVFFCUlI6R2Gqs05HnoQ2mhrU3uFfLx2jwBMakLCjdCaq3uH"
        aksk_config.end_point = "api.cdnetworks.com"
        aksk_config.uri = "/api/report/domainflow?dateFrom=2025-02-26T00%3A00%3A00%2B08%3A00&dateTo=2025-03-04T23%3A59%3A59%2B08%3A00&type="
        aksk_config.method = "POST"

        # See AkSkAuth class for more methods, you can edit
        response = AkSkAuth.invoke(aksk_config, json.dumps(queryDomainTotalTrafficRequest.to_map()))
        print(response)


if __name__ == "__main__":
    Client.main()