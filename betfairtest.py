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



def MockOutBetfairSOAPAPI(function):
    def Mocked(*args):
        oldBetfairSOAPAPI = betfair.BetfairSOAPAPI
        try:
            betfair.BetfairSOAPAPI = mockBetfairSOAPAPI
            function(*args)
        finally:
            betfair.BetfairSOAPAPI = oldBetfairSOAPAPI
    return Mocked


class BetfairGatewayTest(unittest.TestCase):

    @MockOutBetfairSOAPAPI
    def testCreationShouldBindGatewayFields(self):
        gateway = betfair.Gateway()
        self.assertEqual(type(gateway.globalService), MockBFGlobalService)
        self.assertEqual(type(gateway.exchangeService), MockBFExchangeService)


    @MockOutBetfairSOAPAPI
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


    @MockOutBetfairSOAPAPI
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


    @MockOutBetfairSOAPAPI
    def testGetAllMarketsShouldPassSessionToken(self):
        gateway = betfair.Gateway()
        gateway._sessionToken = "12345"
        MockBFExchangeService.test = self
        MockBFExchangeService.expectedSessionToken = gateway._sessionToken
        MockBFExchangeService.getAllMarketsCalled = False
        markets = gateway.getAllMarkets()
        self.assertTrue(MockBFExchangeService.getAllMarketsCalled)



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



if __name__ == '__main__':
    unittest.main()
