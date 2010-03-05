from System import DateTime

import clr
clr.AddReference("betfair")
import BetfairSOAPAPI



def DateTimeFromPosix(milliseconds):
    return DateTime(1970, 1, 1).AddMilliseconds(milliseconds)


def SplitOnDelimiter(delimiter, string):
    words = []
    inEscapedChar = False
    nextWord = []
    for c in string:
        if not inEscapedChar:
            if c == delimiter:
                words.append(''.join(nextWord))
                nextWord = []
                continue
            elif c == '\\':
                inEscapedChar = True
        else:
            inEscapedChar = False
        nextWord.append(c)
    words.append(''.join(nextWord))
    return words


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