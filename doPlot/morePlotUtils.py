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

##cmd_subfolder = os.path.realpath("/afs/cern.ch/user/l/lmcclymo/private/bTrigger_workspace/StudyTrigTracks/StudyTrigTracks/scripts/")
cmd_subfolder = os.path.realpath("/afs/cern.ch/user/l/lmcclymo/private/dijet_workspace/BTaggedDiJet_Run2/Code/trunk/FitStudies/scripts")
sys.path.insert(0, cmd_subfolder)

import doPlotUtils
from doPlotUtils import doPlot

## Setup Area ##

import AtlasStyle
AtlasStyle.SetAtlasStyle()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 3000") #Ignore TCanvas::Print info

ROOT.gStyle.SetOptTitle( 0 )
ROOT.gROOT.SetBatch(True)


########### Define some functions #############

def getFile(fileName, verbose=False):

    file= ROOT.TFile(fileName ,"READ")
    if(verbose):
        print " ** getFile got", file.GetName()
    return file


def getHist(file, histName, outputHistName="", binning="", binning_unit=-1):

    histRaw=file.Get(histName)
    if not histRaw:
        raise SystemExit('\n***ERROR*** histogram not found: '+file.GetName()+':'+histName)

    hist=histRaw
    if binning:
        hist=rebinHist(histRaw,binning,binning_unit)
    
    hist.Sumw2()

    if outputHistName:
        hist.SetName(outputHistName)

    hist.SetDirectory(0)
    return hist


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


def makeRatio(hNum, hDen, ratioOptionRaw=""):

    print "ratioOption", ratioOptionRaw
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
        hDen
        

        if("bayes" in ratioOption): doBayes="Bayes"
        else:                       doBayes=""
        ratioHist=makeRatio(hNum,hDen,doBayes)
        return ratioHist

    
    if ("zero" in ratioOption):     
        if ("num" in ratioOption):
            print "Setting errors in den to zero"
            hDen=setErrorsToZero(hDen)
        elif ("den" in ratioOption):
            print "Setting errors in num to zero"
            hNum=setErrorsToZero(hNum)
        else:
            print "Error in makeRatio, if option 'zero' then must specify 'zeroden' or 'zeronum'"
            return

    if("bayes" in ratioOption):
        doBayes="Bayes"
        ratioHist=makeRatio(hNum,hDen,doBayes)
        return ratioHist       
        
    else:
        ratioHist=hNum.Clone(hDen.GetName()+"_ratio")
        ratioHist.Sumw2()
        ratioHist.Divide(hDen)
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
                 
def doRatioPlot ( listOfHistListsRaw, plotName, genOptionString="", ratioOption="", binning="", binning_unit=-1):

    listOfHistLists=[]
    listOfHistLists=listOfHistLists+listOfHistListsRaw
    print "length - ", len(listOfHistListsRaw)
    
    for iHist,histList in enumerate(listOfHistListsRaw):

        print histList

        try:
            ratioError=str(genOptionString.split("RatioError:")[1].split(",")[0])
        except:
            ratioError=""
            
        print "histList[0]", histList[0]
        print "listOfHistLists[0][0]", listOfHistLists[0][0]
        print
        ratio=makeRatio(histList[0],listOfHistLists[0][0],ratioError)
                
        option=""
        if ratioOption:
            option+=","+ratioOption
        if "colour:" in histList[1]:
            option+=',colour:'+histList[1].split("colour:")[1]

        if iHist==0:
            option=",fillStyle:dots,drawOption:E2"+option
            
        ratioList=[ratio,"pad:2"+option]
        print "ratio Options", ratioList[1]
        listOfHistLists.append(ratioList)
        #break
            
    optionString="plotName:"+plotName+",legend:yesPlease"
    if(genOptionString):
        optionString+=","+genOptionString

    print
    print "doRatioPlot:"
    print " -> listOfHistLists: ", listOfHistLists
    print " -> optionSting:     ",optionString
    doPlot( listOfHistLists, optionString )
    print " done doPlot "
    print; print;

    return
