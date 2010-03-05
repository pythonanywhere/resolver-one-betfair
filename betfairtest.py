import unittest

from System import DateTime


import betfair
import BetfairSOAPAPI


class MockBFGlobalService(object):
    def login(self, request):
        MockBFGlobalService.test.assertEqual(request.username, MockBFGlobalService.expectedUsername)
        MockBFGlobalService.test.assertEqual(request.password, MockBFGlobalService.expectedPassword)
        MockBFGlobalService.test.assertEqual(request.productId, 82)
        if MockBFGlobalService.success:
            errorCode = BetfairSOAPAPI.LoginErrorEnum.OK
        else:
            errorCode = BetfairSOAPAPI.LoginErrorEnum.INVALID_USERNAME_OR_PASSWORD
        header = BetfairSOAPAPI.APIResponseHeader1(sessionToken=MockBFGlobalService.sessionToken)
        return BetfairSOAPAPI.LoginResp(errorCode=errorCode, header=header)


class MockBFExchangeService(object):
    def getAllMarkets(self, request):
        MockBFExchangeService.getAllMarketsCalled = True
        MockBFExchangeService.test.assertEqual(
            MockBFExchangeService.expectedSessionToken,
            request.header.sessionToken
        )


class MockBetfairSOAPAPI(object):
    BFGlobalService = MockBFGlobalService
    BFExchangeService = MockBFExchangeService

    APIRequestHeader = BetfairSOAPAPI.APIRequestHeader

    LoginReq = BetfairSOAPAPI.LoginReq
    LoginErrorEnum = BetfairSOAPAPI.LoginErrorEnum

    GetAllMarketsReq = BetfairSOAPAPI.GetAllMarketsReq

mockBetfairSOAPAPI = MockBetfairSOAPAPI()



def MockOut(**kwargs):
    def Decorator(function):
        def Decorated(*_args, **_kwargs):
            oldValues = {}
            for key, _ in kwargs.items():
                oldValues = getattr(betfair, key)
            try:
                for key, newValue in kwargs.items():
                    setattr(betfair, key, newValue)
                function(*_args, **_kwargs)
            finally:
                for key, oldValue in kwargs.items():
                    setattr(betfair, key, oldValue)
        return Decorated
    return Decorator


class BetfairGatewayTest(unittest.TestCase):

    def testDateTimeFromPosix(self):
        self.assertEquals(DateTime(1970, 1, 1), betfair.DateTimeFromPosix(0))
        self.assertEquals(DateTime(1970, 1, 1, 1, 0, 0), betfair.DateTimeFromPosix(3600000))
        self.assertEquals(DateTime(1970, 1, 2), betfair.DateTimeFromPosix(3600000*24))
        self.assertEquals(DateTime(1971, 1, 1), betfair.DateTimeFromPosix(3600000*24*365))
        self.assertEquals(DateTime(1979, 12, 30), betfair.DateTimeFromPosix(3600000*24*365*10))


    def testSplitOnDelimiter(self):
        self.assertEquals(["a", "b"], betfair.SplitOnDelimiter(":", "a:b"))
        self.assertEquals(["a\\:b", "c"], betfair.SplitOnDelimiter(":", "a\\:b:c"))
        self.assertEquals(["", "a", "b"], betfair.SplitOnDelimiter(":", ":a:b"))


    def testMarketFromRecordString(self):
        market = betfair.Market.fromRecordString(
            "12~"
            "Market \\~ name~"
            "Type~"
            "Status~"
            "31536000000~"
            "\\Menu\\Path\\To\\Market~"
            "event hierarchy~"
            "bet delay~"
            "12345~"
            "country code~"
            "94608000000~"
            "55~"
            "2~"
            "1.234556~"
            "N~"
            "Y"
        )
        self.assertEquals(market.Id, 12)
        self.assertEquals(market.Name, "Market \\~ name")
        self.assertEquals(market.Type, "Type")
        self.assertEquals(market.Status, "Status")
        self.assertEquals(market.StartDate, DateTime(1971, 1, 1))
        self.assertEquals(market.Path, "\\Menu\\Path\\To\\Market")
        self.assertEquals(market.EventHierarchy, "event hierarchy")
        self.assertEquals(market.BetDelay, "bet delay")
        self.assertEquals(market.ExchangeId, 12345)
        self.assertEquals(market.CountryCode, "country code")
        self.assertEquals(market.LastRefresh, DateTime(1972, 12, 31))
        self.assertEquals(market.NumberOfRunners, 55)
        self.assertEquals(market.NumberOfWinners, 2)
        self.assertEquals(market.TotalAmountMatched, 1.234556)
        self.assertEquals(market.BSPMarket, False)
        self.assertEquals(market.TurningInPlay, True)



    @MockOut(BetfairSOAPAPI=mockBetfairSOAPAPI)
    def testCreationShouldBindGatewayFields(self):
        gateway = betfair.Gateway()
        self.assertEqual(type(gateway.globalService), MockBFGlobalService)
        self.assertEqual(type(gateway.exchangeService), MockBFExchangeService)


    @MockOut(BetfairSOAPAPI=mockBetfairSOAPAPI)
    def testLoginShouldReturnTrueAndSetSessionTokenWhenSuccessful(self):
        gateway = betfair.Gateway()
        MockBFGlobalService.test = self
        MockBFGlobalService.success = True
        MockBFGlobalService.expectedUsername = "harold"
        MockBFGlobalService.expectedPassword = "s3kr1t"
        MockBFGlobalService.sessionToken = "12345"
        result = gateway.login(MockBFGlobalService.expectedUsername, MockBFGlobalService.expectedPassword)
        self.assertTrue(result)
        self.assertEquals(gateway._sessionToken, MockBFGlobalService.sessionToken)


    @MockOut(BetfairSOAPAPI=mockBetfairSOAPAPI)
    def testLoginShouldReturnFalseAndClearSessionTokenWhenUnsuccessful(self):
        gateway = betfair.Gateway()
        MockBFGlobalService.test = self
        MockBFGlobalService.success = False
        MockBFGlobalService.expectedUsername = "harold"
        MockBFGlobalService.expectedPassword = "s3kr1t"
        MockBFGlobalService.sessionToken = "12345"
        result = gateway.login(MockBFGlobalService.expectedUsername, MockBFGlobalService.expectedPassword)
        self.assertFalse(result)
        self.assertEquals(gateway._sessionToken, None)


    @MockOut(BetfairSOAPAPI=mockBetfairSOAPAPI)
    def testGetAllMarketsShouldPassSessionToken(self):
        gateway = betfair.Gateway()
        gateway._sessionToken = "12345"
        MockBFExchangeService.test = self
        MockBFExchangeService.expectedSessionToken = gateway._sessionToken
        MockBFExchangeService.getAllMarketsCalled = False
        markets = gateway.getAllMarkets()
        self.assertTrue(MockBFExchangeService.getAllMarketsCalled)




if __name__ == '__main__':
    unittest.main()
