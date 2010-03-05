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


class Market(object):
    @classmethod
    def fromRecordString(cls, recordString):
        fields = SplitOnDelimiter('~', recordString)
        market = cls()

        market.Id = int(fields[0])
        market.Name = fields[1]
        market.Type = fields[2]
        market.Status = fields[3]
        market.StartDate = DateTimeFromPosix(int(fields[4]))
        market.Path = fields[5]
        market.EventHierarchy = fields[6]
        market.BetDelay = fields[7]
        market.ExchangeId = int(fields[8])
        market.CountryCode = fields[9]
        market.LastRefresh = DateTimeFromPosix(int(fields[10]))
        market.NumberOfRunners = int(fields[11])
        market.NumberOfWinners = int(fields[12])
        market.TotalAmountMatched = float(fields[13])
        market.BSPMarket = fields[14] == "Y"
        market.TurningInPlay = fields[15] == "Y"
        return market

    def __str__(self):
        return "Market: %s" % (self.Name, )


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
        response = self.exchangeService.getAllMarkets(request)
        return [Market.fromRecordString(data) for data in SplitOnDelimiter(':', response.marketData)]