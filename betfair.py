import clr
clr.AddReference("betfair")
import BetfairSOAPAPI


class Gateway(object):

    def __init__(self):
        self.globalService = BetfairSOAPAPI.BFGlobalService()
        self.exchangeService = BetfairSOAPAPI.BFExchangeService()


    def login(self, username, password):
        loginReq = BetfairSOAPAPI.LoginReq(username=username, password=password, productId=82)
        response = self.globalService.login(loginReq)
        if response.errorCode == BetfairSOAPAPI.LoginErrorEnum.OK:
            self._sessionToken = response.header.sessionToken
            return True
        self._sessionToken = None
        return False


    def getAllMarkets(self):
        request = BetfairSOAPAPI.GetAllMarketsReq()
        request.header = BetfairSOAPAPI.APIRequestHeader(sessionToken=self._sessionToken)
        self.exchangeService.getAllMarkets(request)