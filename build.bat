wsdl /namespace:BetfairSOAPAPI BFGlobalService.wsdl BFExchangeService.wsdl
csc /target:library /out:betfair.dll BFGlobalService.cs
