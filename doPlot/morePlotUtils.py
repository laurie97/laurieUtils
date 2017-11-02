#############################################
#
# morePlotUtils.py
#
# => What's in here
#
# - doCominedPlot
# - doCombinedPlotRatio
#
#
#############################################

import ROOT
import argparse
from argparse import RawTextHelpFormatter
import os, sys
import array
from   math  import sqrt
from collections import defaultdict

##cmd_subfolder = os.path.realpath("/afs/cern.ch/user/l/lmcclymo/public/bTrigger_workspace/StudyTrigTracks/StudyTrigTracks/scripts/")
##cmd_subfolder = os.path.realpath("/afs/cern.ch/user/l/lmcclymo/public/dijet_workspace/BTaggedDiJet_Run2/Code/trunk/FitStudies/scripts")
cmd_subfolder = os.path.realpath("/afs/cern.ch/user/l/lmcclymo/public/laurieUtils/doPlot/")
sys.path.insert(0, cmd_subfolder)

import doPlotUtils
from doPlotUtils import doPlot

## Setup Area ##

import AtlasStyle
AtlasStyle.SetAtlasStyle()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 3000") #Ignore TCanvas::Print info
ROOT.gStyle.SetOptTitle( 0 )
ROOT.gROOT.SetBatch(True)

verbose=False

########### Define some functions #############

def getFile(fileName, verbose=False):

    file= ROOT.TFile(fileName ,"READ")
    if(verbose):
        print " ** getFile got", file.GetName()
    return file

def makeFile(fileName, verbose=False):

    file= ROOT.TFile(fileName ,"RECREATE")
    if(verbose):
        print " ** makeFile got", file.GetName()
    return file

def getHist(file, histName, outputHistName="", binning="", binning_unit=-1):

    histRaw=file.Get(histName)
    if not histRaw:
        raise SystemExit('\n***ERROR*** histogram not found: '+file.GetName()+':'+histName)

    if not binning:
        hist=histRaw
    else:
        hist=rebinHist(histRaw,binning,binning_unit)
    
    hist.Sumw2()

    
    if outputHistName:
        hist.SetName(outputHistName)

    hist.SetDirectory(0)
    return hist

def getGraph(file, graphName, outputGraphName=""):

    graphRaw=file.Get(graphName)
    if not graphRaw:
        raise SystemExit('\n***ERROR*** graphogram not found: '+file.GetName()+':'+graphName)

    graph=graphRaw
    
    if outputGraphName:
        graph.SetName(outputGraphName)

    return graph


def graphToHist(graph, hist):

    for i in range(graph.GetN()):
        x = ROOT.Double()
        y = ROOT.Double()
        graph.GetPoint(i, x, y)

        histBin = hist.FindBin(x)

        elow  = graph.GetErrorYlow(i)
        ehigh = graph.GetErrorYhigh(i)
        error = (elow + ehigh)/2.

        content =  y
        
        hist.SetBinContent(histBin, content)
        hist.SetBinError  (histBin, error)


def makeSig(hDataRaw, hBkgRaw, sigOptionRaw=""):

    sigOptionRaw+="error"
    if(verbose): print "  makeSig: sigOption", sigOptionRaw
    # No case sensitivity
    sigOption=sigOptionRaw.lower()

    if("reverse" in sigOptionRaw):
        #print "!!!! reverse"
        hData=hBkgRaw
        hBkg=hDataRaw
    else:
        hData=hDataRaw
        hBkg=hBkgRaw
   
    hSig=hBkgRaw.Clone()
    for iBin in range(hBkg.GetNbinsX()):
   
        if( ("error" in sigOptionRaw) and hBkg.GetBinError(iBin) > 0):
            
            #if(hData.GetBinContent > 0):
            #    print "makeSig: iBin {}: ({}-{})/{} =".format(iBin,hData.GetBinContent(iBin),hBkg.GetBinContent(iBin),hBkg.GetBinError(iBin)),
            #    print (hData.GetBinContent(iBin)-hBkg.GetBinContent(iBin))/hBkg.GetBinError(iBin)
            hSig.SetBinContent(iBin,  (hData.GetBinContent(iBin)-hBkg.GetBinContent(iBin))/hBkg.GetBinError(iBin) )
            hSig.SetBinError(  iBin,  0 )
            continue
            
        elif (  hBkg.GetBinContent(iBin) > 0):
            hSig.SetBinContent(iBin,  (hData.GetBinContent(iBin)-hBkg.GetBinContent(iBin))/sqrt(hBkg.GetBinContent(iBin)) )
            hSig.SetBinError(  iBin,  0 )
            continue
        
        hSig.SetBinContent(iBin,  0 )
        hSig.SetBinError(  iBin,  0 )
            
    return hSig

        
def makeRatio(hNum, hDen, ratioOptionRaw=""):

    #print "ratioOption", ratioOptionRaw
    # No case sensitivity
    ratioOption=ratioOptionRaw.lower()
    
    if ratioOption=="bayes":
        print "Doing bayesian errors"
        ratioGraph = ROOT.TGraphAsymmErrors()#num.GetNbinsX())
        ratioGraph.BayesDivide(hNum,hDen)
        ratioHist = hNum.Clone(hDen.GetName()+"_ratioBayes")        
        graphToHist(ratioGraph,ratioHist)
        return ratioHist
        
    if ("matchbinning" in ratioOption):
        print "Match binning"
        hNumChange=hDen.Clone()
        for iBin in range(hDen.GetNbinsX()):
            print " - ",iBin, hNum.GetBinContent(hNum.FindBin(hDen.GetBinCenter(iBin)))
            hNumChange.SetBinContent(iBin, hNum.GetBinContent(hNum.FindBin(hDen.GetBinCenter(iBin)) ) )
            hNumChange.SetBinError(  iBin, hNum.GetBinError(  hNum.FindBin(hDen.GetBinCenter(iBin)) ) )
        hNum=hNumChange
    
    if ("zero" in ratioOption):     
        if ("num" in ratioOption):
            if(verbose): print " makeRatio: Setting errors in den to zero"
            hDen=setErrorsToZero(hDen)
        elif ("den" in ratioOption):
            if(verbose): print " makeRatio: Setting errors in num to zero"
            hNum=setErrorsToZero(hNum)
        else:
            if(verbose): print " makeRatio: Error in makeRatio, if option 'zero' then must specify 'zeroden' or 'zeronum'"
            return

    if("bayes" in ratioOption):
        doBayes="Bayes"
        ratioHist=makeRatio(hNum,hDen,doBayes)
        return ratioHist       
        
    else:
        ratioHist=hNum.Clone(hDen.GetName()+"_ratio")
        try: ratioHist.Sumw2()
        except: print "makeRatio: warning, not setting Sumw2, might be a function"
        ratioHist.Divide(hDen)
        #for iBin in range(1,ratioHist.GetNbinsX()+1):
        #    if(ratioHist.GetBinContent(iBin) > 0):
        #        sig=(ratioHist.GetBinContent(iBin)-1)/ratioHist.GetBinError(iBin)
        #        print "makeRatio: iBin {}: ({} +/- {}) => Sig {}".format(iBin,ratioHist.GetBinContent(iBin),ratioHist.GetBinError(iBin),sig)
        return ratioHist

   


def setErrorsToZero(hRaw):
    hOut=hRaw.Clone(hRaw.GetName()+"_zeroError")
    for bin in range(hOut.GetNbinsX()+1):
        hOut.SetBinError(bin,0)
    return hOut

#def doFit(hist, option="linear", xLow, xUp):
def doFit(hist, option, xLow, xUp):

    fitFunction=""

    if option=="flat":
        fitFunction=ROOT.TF1("fitFunction_flat_"+hist.GetName(), "[0]", xLow , xUp )
        fitFunction.SetParameter(0,1)
    
    if option=="linear":
        fitFunction=ROOT.TF1("fitFunction_line_"+hist.GetName(), "[0]+[1]*x", xLow , xUp )
        fitFunction.SetParameters(1,1)

    if option=="quad":
        fitFunction=ROOT.TF1("fitFunction_quad_"+hist.GetName(), "[0]+[1]*x+[2]*x^2",  xLow , xUp )
        fitFunction.SetParameters(1,1,1)

    if option=="poly3":
        fitFunction=ROOT.TF1("fitFunction_poly3_"+hist.GetName(), "[0]+[1]*x+[2]*x^2+[3]*x^3",  xLow , xUp )
        fitFunction.SetParameters(1,1,1,-1)

    if option=="poly4":
        fitFunction=ROOT.TF1("fitFunction_poly3_"+hist.GetName(), "[0]+[1]*x+[2]*x^2+[3]*x^3",  xLow , xUp )
        fitFunction.SetParameters(1,1,1,-1)


def correctForFit(inEff, inFit, xCut=0, correctionName="correction"):

    outEff = inEff.Clone(inEff.GetName()+"_"+correctionName)
    
    #
    #  Shape uncertianty
    #
    
    for i in range(inEff.GetNbinsX()+1):
        thisX = inEff.GetBinCenter(i)
        if thisX < xCut: continue 

        ## If it is a fit.
        try:
            fitVal = inFit .Eval(thisX)
        ## Could also be a histogram...
        except:
            fitVal = inFit.GetBinContent(inFit.FindBin(thisX))
            
        oldEff = inEff.GetBinContent(i)
        newEff = oldEff * fitVal

        oldErr = inEff.GetBinError(i)
        newErr = oldErr * fitVal

        
        outEff.SetBinContent(i, newEff)
        outEff.SetBinError(i, newErr)

    return outEff

def funcToHist(func, cloneHist):

    hist=cloneHist.Clone("h_"+func.GetName())

    print "h_"+func.GetName()
    for bin in range(hist.GetNbinsX()+1):
        center=hist.GetBinCenter(bin)
        cont=func.Eval(center)
        #if  center < xLow or center > xUp: cont=0
        hist.SetBinContent(bin, cont)
        hist.SetBinError(bin,0)
        ##print " ", bin, hist.GetBinCenter(bin), cont
        hist.Sumw2()

    return hist


def doListMagic(fileListRaw, histNameListRaw):

    print 'fileListRaw', fileListRaw
    print 'histNameListRaw', histNameListRaw
    
    if not ( isinstance(fileListRaw, list) or isinstance(histNameListRaw, list) ):
        histNameList = [ histNameListRaw ]
        fileList     = [ fileListRaw ]
     
    elif not (isinstance(fileListRaw, list)):
        fileList=[]
        for histName in histNameListRaw:
            fileList.append(fileListRaw)
        histNameList=histNameListRaw

    elif not (isinstance(histNameListRaw, list)):
        histNameList=[]
        for file in fileListRaw:
            histNameList.append(histNameListRaw)
        fileList=fileListRaw
    
    elif( len(fileListRaw) == len(histNameListRaw) ):
        return fileListRaw, histNameListRaw
    
    else:
        raise SystemExit('\n***ERROR*** doListMagic: No magic here len(fileListRaw) != len(histNameListRaw), and both are lists\n')
        

    return fileList, histNameList

def rebinHist(hRaw,binning,perUnit=-1):

    print "Rebinning hist", hRaw.GetName(), hRaw.GetNbinsX()
    try:
        hNew=hRaw.Rebin( (len(binning)-1), "hNew", binning)
    except TypeError:
        hNew=hRaw.Rebin( binning, "hNew")
    
    if perUnit > 0:
      for bin in range(hNew.GetNbinsX()):
        oldCont=hNew.GetBinContent(bin)
        width  =hNew.GetBinWidth(bin)
        newCont=(oldCont*perUnit)/width
        hNew.SetBinContent(bin, newCont)
        
    hNew.SetName(hRaw.GetName())
    print "Rebined hist", hNew.GetName(), hNew.GetNbinsX()
    return hNew



def doCombinedRatioPlot( fileNameListRaw, histNameListRaw, plotName, genOptionString="", histOptionList="", ratioOption="", binning="", binning_unit=-1):

    (fileNameList, histNameList) = doListMagic( fileNameListRaw, histNameListRaw)

    fileList=[]
    for fileName in fileNameList:
        fileList.append( getFile(fileName,True) )

    ratioHistName=histNameList[0]
    ratioHist=getHist(fileList[0],ratioHistName,ratioHistName+"_"+plotName+"_0",binning,binning_unit)

    listOfHistLists=[]
    for iFile,file in enumerate(fileList):

        if iFile==0: continue
        
        numName=histNameList[iFile]
        num=getHist(file,numName,numName+"_"+plotName+"_"+str(iFile),binning,binning_unit)

        try:
            ratioError=str(histOptionList[iFile].split("RatioError:")[1].split(",")[0])
        except:
            ratioError=""       
        print "upper panel ratio for ",iFile," options is ",ratioError
        hist=makeRatio(num,ratioHist,ratioError)

        option=""
        if histOptionList:
            option=','+histOptionList[iFile]
            
        histList=[hist,"markerStyle:Square,pad:1"+option]
        listOfHistLists.append(histList)
        print histList

        if iFile > 1:
            
            print "Make a ratio"
            
            try:
                ratioError=str(genOptionString.split("RatioError:")[1].split(",")[0])
            except:
                ratioError=""
            print "lower panel ratio for ",iFile," options is ",ratioError
            ratio=makeRatio(hist,listOfHistLists[0][0],ratioError)
                
            option=""
            if ratioOption:
                option+=","+ratioOption
            if histOptionList:
                option+=',colour:'+histOptionList[iFile].split("colour:")[1]
                
            ratioList=[ratio,"pad:2"+option]
            print "ratio Options", ratioList[1]
            listOfHistLists.append(ratioList)

    optionString="plotName:"+plotName+",legend:yesPlease"
    if(genOptionString):
        optionString+=","+genOptionString

    print
    print "doPlot:"
    print " -> listOfHistLists: ", listOfHistLists
    print " -> optionSting:     ",optionString
    doPlot( listOfHistLists, optionString )
    print " done doPlot "
    print; print;
            

def doCombinedPlotFromFile( fileNameListRaw, histNameListRaw, plotName, genOptionString="", histOptionList="", ratioOption="", binning="", binning_unit=-1):
    
    # Return the list given, or return the string in a list form to suit
    (fileNameList, histNameList) = doListMagic( fileNameListRaw, histNameListRaw)

    fileList=[]
    for fileName in fileNameList:
        fileList.append( getFile(fileName,True) )
        
    listOfHistLists=[]
    for iFile,file in enumerate(fileList):

        histName=histNameList[iFile]
        hist=getHist(file,histName,histName+"_"+plotName+"_"+str(iFile),binning,binning_unit)

        option=""
        if histOptionList:
            option=','+histOptionList[iFile]
            
        histList=[hist,"markerStyle:Square,pad:1"+option]
        listOfHistLists.append(histList)
        print histList

    doRatioPlot( listOfHistLists, plotName, genOptionString, ratioOption, binning, binning_unit)
    return


def doRatioAndSigPlot ( listOfHistListsRaw, plotName, genOptionString="", ratioOption="", sigOption="yRange:-3;3", binning="", binning_unit=-1):

    
    if not (isinstance(ratioOption, list)):
        doRatioPlot        ( listOfHistListsRaw, plotName,        genOptionString+",RatioError:zeronum", ratioOption, binning, binning_unit)
    else:
        for iRatioOption, thisRatioOption in enumerate(ratioOption):
            if(iRatioOption==0):
                doRatioPlot ( listOfHistListsRaw, plotName,        genOptionString+",RatioError:zeronum", thisRatioOption, binning, binning_unit)       
            else:
                print "LM Debug:", thisRatioOption, thisRatioOption.replace(".","p").replace(";","_").replace(":","_")                
                doRatioPlot ( listOfHistListsRaw, plotName+"_ratio_"+thisRatioOption.replace(".","p").replace(";","_").replace(":","_"),
                              genOptionString+",RatioError:zeronum",
                              thisRatioOption,  binning, binning_unit)
               
        
        
    if not (isinstance(sigOption, list)):
        doSignificancePlot ( listOfHistListsRaw, plotName+"_sig", genOptionString, sigOption,   binning, binning_unit)
    else:
        for iSigOption, thisSigOption in enumerate(sigOption):
            if(iSigOption==0):
                doSignificancePlot ( listOfHistListsRaw, plotName+"_sig", genOptionString, thisSigOption,   binning, binning_unit)
            else:
                print "LM Debug:", thisSigOption, thisSigOption.replace(".","p").replace(";","_").replace(":","_")
                doSignificancePlot ( listOfHistListsRaw, plotName+"_sig_"+thisSigOption.replace(".","p").replace(";","_").replace(":","_"),
                                     genOptionString, thisSigOption,   binning, binning_unit)

                 
def doRatioPlot ( listOfHistListsRaw, plotName, genOptionString="", ratioOption="", binning="", binning_unit=-1):

    listOfHistLists=[]
    listOfHistLists=listOfHistLists+listOfHistListsRaw
    #print "length - ", len(listOfHistListsRaw)

    hDen=listOfHistLists[0][0]
    if( "type:function" in listOfHistLists[0][1].lower() ):
        print " I do know it's a function!!!"
        try:     hDen=funcToHist(hDen,listOfHistLists[1][0])
        except:  hDen=funcToHist(hDen,listOfHistLists[2][0])
    
    for iHist,histList in enumerate(listOfHistListsRaw):

        #print histList

        try:
            ratioError=str(genOptionString.split("RatioError:")[1].split(",")[0])
        except:
            ratioError=""
            
        #print "histList[0]", histList[0]
        #print "listOfHistLists[0][0]", listOfHistLists[0][0]
        #print
        hNum=histList[0]
        if( "type:function" in histList[1].lower() ):
            hNum=funcToHist(hNum,hDen)
        
        ratio=makeRatio(hNum,hDen,ratioError)
        
        option=""
        if ratioOption:
            option+=","+ratioOption
        if "colour:" in histList[1]:
            option+=',colour:'+histList[1].split("colour:")[1]

        if (iHist==0 and not ("type:function" in histList[1].lower() ) ):
            option=option.replace(",drawOption:Hist","")
            option=option.replace(",markerStyle:",",blankOption:")
            option+=",fillStyle:dots,drawOption:E2"
            if(verbose): print " doRatioPlot: ratioOption for ratioHist", option

        #if (iHist!=0 and "zero" in ratioError):
        if (iHist!=0 and ("type:function" in histList[1].lower()) ):
            #option=option.replace(",drawOption:",",blankOption:") 
            #option+=",drawOption:Hist"
            if(verbose): print " doRatioPlot: ratioOption for ratioHist", option

       
        ratioList=[ratio,"pad:2"+option]
        #print "ratio Options", ratioList[1]
        listOfHistLists.append(ratioList)
        #break
            
    optionString="plotName:"+plotName+",legend:yesPlease"
    if(genOptionString):
        optionString+=","+genOptionString

    if("verbose" in genOptionString):
        print
        print "doRatioPlot:"
        print " -> listOfHistLists: ", listOfHistLists
        print " -> optionSting:     ",optionString
    doPlot( listOfHistLists, optionString )


    return



def doSignificancePlot ( listOfHistListsRaw, plotName, genOptionString="", sigOption="", binning="", binning_unit=-1):

    listOfHistLists=[]
    listOfHistLists=listOfHistLists+listOfHistListsRaw
    #print "length - ", len(listOfHistListsRaw)

    try:     sigIndex=int(genOptionString.split("SigIndex:")[1].split(",")[0])
    except:  sigIndex=0

    try:      makeSigOption=str(genOptionString.split("SigOption:")[1].split(",")[0])
    except:   makeSigOption=""

    if(verbose): print "  doSigPlot: GenOptionStr",genOptionString
    if(verbose): print "  doSigPlot: myOptions: makeSigOption {}, sigIndex {}".format(makeSigOption,sigIndex)

    ## Make the labelled index as bkg (i.e. base of the calculation)
    hBkg=listOfHistLists[sigIndex][0]
    if( "type:function" in listOfHistLists[sigIndex][1].lower() ):
        hBkg=funcToHist(hBkg,hData)

    
    for iHist,histList in enumerate(listOfHistListsRaw):

        #print histList
        ##
        hData=histList[0]
        if( "type:function" in histList[1].lower() ):
            hData=funcToHist(hBkg,hData)
            
        #print "histList[0]", histList[0]
        #print "hData", hData
        sig=makeSig(hData,hBkg,makeSigOption)
        
        option=""
        if sigOption:
            option+=","+sigOption
        if "colour:" in histList[1]:
            option+=',colour:'+histList[1].split("colour:")[1]

        if iHist==sigIndex:
            option=",fillStyle:dots,drawOption:E2"+option
            
        sigList=[sig,"pad:2"+option]
        #print "sig Options", sigList[1]
        listOfHistLists.append(sigList)
        #break
            
    optionString="plotName:"+plotName+",legend:yesPlease,ratio_yTitle:Sig."
    if(genOptionString):
        optionString+=","+genOptionString

    if("verbose" in genOptionString):
        print
        print "doSigPlot:"
        print " -> listOfHistLists: ", listOfHistLists
        print " -> optionSting:     ",optionString
    doPlot( listOfHistLists, optionString )

    return

def doPad1Plot(listOfHistLists, optionString ):

    if not ("nPads" in optionString):         optionString+=",nPads:1"
    if not ("atlasLabelPos" in optionString): optionString+=",atlasLabelPos:0.2-0.85"
    if not ("plotStringPos" in optionString): optionString+=",plotStringPos:0.2-0.7-0.85"
    if not ("yTitleSize" in optionString):    optionString+=",yTitleSize:0.05"
    if not ("yTitleSize" in optionString):    optionString+=",xTitleSize:0.05"

    doPlot( listOfHistLists, optionString )
