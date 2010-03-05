import unittest

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
    pass


class MockBetfairSOAPAPI(object):
    BFGlobalService = MockBFGlobalService
    BFExchangeService = MockBFExchangeService
    LoginReq = BetfairSOAPAPI.LoginReq
    LoginErrorEnum = BetfairSOAPAPI.LoginErrorEnum
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


if __name__ == '__main__':
    unittest.main()
