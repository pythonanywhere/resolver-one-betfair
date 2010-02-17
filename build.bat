wsdl /namespace:Betfair BFGlobalService.wsdl BFExchangeService.wsdl
csc /target:library /out:betfair.dll BFGlobalService.cs
