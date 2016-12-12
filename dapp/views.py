#Django
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django import forms
from django.views.decorators.csrf import csrf_exempt

#System
import json
import os
import re
import urllib
import json
import os
import uuid 
import shutil
from datetime import datetime
from os import path

#Custom / Thirdparty
from thirdparty import test
from thirdparty.temoa.db_io import Make_Graphviz
from handle_modelrun import run_model
from thirdparty.temoa.temoa_model import get_comm_tech

from thirdparty.temoa.db_io.db_query import get_flags

def login(request):
  return render_to_response('login.html', context_instance=RequestContext(request))

def inputData(request):

  random = str(uuid.uuid4().get_hex().upper()[0:6])

  return render_to_response('InputData.html', { 'mode' : 'input' , 'random' : random,  'title' : 'Input Data'}, context_instance=RequestContext(request))

def outputData(request):
  return render_to_response('InputData.html', { 'mode' : 'output' , 'title' : 'Output Data'}, context_instance=RequestContext(request))

def modelRun(request):
  return render_to_response('ModelRun.html', { 'title' : 'Model Run'} , context_instance=RequestContext(request))

def _getLog():
  originalLogFile = settings.RESULT_DIR +  "debug_logs/OutputLog.log"
  archiveLogFile = settings.RESULT_DIR + "debug_logs/OutputLog__"+str(datetime.now().date()) + "__" +str(datetime.now().time())+".log"

  file = open(originalLogFile, 'r')

  if not file:
    return "Log not found or created"

  output = file.read()

  #Maintain archive of current log file
  fileArch = open(archiveLogFile, "w")
  fileArch.write(output)

  return output


def runModel(request):
  
  msg = 'Successfully generated'
  result = True
  generatedfolderpath = ''
  zip_path = ''
  outputFilename = request.POST.get("outputdatafilename")
  
  #try:
    #This function will handle 
    #TODO try catch handling
  generatedfolderpath = run_model(request)
  
  #if not generatedfolderpath:
  #  raise "Error detected"
  zip_path = ""
  
  if outputFilename:
    random = str(uuid.uuid4().get_hex().upper()[0:6])
    output_dirname = 'db_io/db_io_' + random 
    #print "Zipping: " + settings.BASE_DIR + "/" + generatedfolderpath + " | " + output_dirname
    if path.exists(generatedfolderpath) and path.exists(settings.RESULT_DIR + output_dirname ):
      shutil.make_archive( settings.RESULT_DIR + output_dirname , 'zip', generatedfolderpath)
    
      zip_path = output_dirname + ".zip"
      
    else:
      msg = "Failed to generate"
  
  #except:
  #  msg = 'An error occured. Please try again.'
  #  result = False
  
    return JsonResponse( {"result" : result , "message" : msg , 'zip_path' : zip_path, "output" : _getLog()  } )
  


def index(request):
  return HttpResponse("Nothing for now...")


def about(request):
  return render_to_response('About-Us.html', context_instance=RequestContext(request))


#get posted data
def runInput(request):
  
  if request.method != 'POST':
    return HttpResponse("Use post method only", status = 403)
  
  
  format = request.POST.get("format", "svg")
  colorscheme = request.POST.get("colorscheme", "color")
  type =request.POST.get("commodity-technology-type", "")
  value =request.POST.get("commodity-technology-value", "")
  filename =request.POST.get("datafile", "")
  mode =request.POST.get("mode", "")

  random =request.POST.get("scenario-name", "")
  dateRange =request.POST.get("date-range", "")
  
  folder, file_extension = os.path.splitext(filename)
  
  
  imagepath = ""
    
  #fulldirpath = os.path.dirname(os.path.abspath(__file__))
  #print settings.BASE_DIR
  #filename = "/home/yash/Projects/dapp/thirdparty/temoa/db_io/temoa_utopia.sqlite"
  #if opt in ("-i", "input"):
    #ifile = arg
  #elif opt in ("-f", "--format"):
    #graph_format = arg
  #elif opt in ("-c", "--show_capacity"):
    #show_capacity = True
  #elif opt in ("-v", "--splinevar") :
    #splinevar = True
  #elif opt in ("-t", "--graph_type") :
    #graph_type = arg
  #elif opt in ("-s", "--scenario") :
    #scenario = arg
  #elif opt in ("-n", "--name") :
    #quick_name = arg
  #elif opt in ("-o", "--output") :
    #res_dir = arg
  #elif opt in ("-g", "--grey") :
    
  inputs = { 
            "-i" : settings.UPLOADED_DIR + filename , 
            "-f" : format,
            "-o" : settings.RESULT_DIR  + mode
  }
          
  if( colorscheme == "grey"):
    inputs['-g'] = colorscheme
    
    

  if mode == "input":
    
    inputs["-n"]= random
    
    imagepath = folder + "_" + random + "/" + folder + "_" + random + ".svg"

  elif mode == "output":

    inputs["--scenario"] = random

    imagepath = folder + "_" + random + "/results/results"+ dateRange +".svg"

    
  if type == 'commodity':
  
    inputs["--comm"] = value
    imagepath = folder + "_" + random + "/commodities/rc_" + value + "_" + dateRange + ".svg" if mode == "output" else folder + "_" + random + "/" + folder + "_" + random + ".svg"
    

  elif type == 'technology':
  
    inputs["--tech"] = value
    #imagepath = 
    imagepath = folder + "_" + random + "/results/results_" + value + "_" + dateRange + ".svg" if mode == "output" else folder + "_" + random + "/" + folder + "_" + random + ".svg"
    
  print inputs

  output_dirname = inputs['-o']+"/"+folder + "_" + random
  #remove existing folder
  
  
  error = ''
  try:  
    
    shutil.rmtree(output_dirname, ignore_errors=True)
  
    makeGraph(inputs)
  except:
    error = 'An error occured. Please try again.'
    

  print "Zipping: " + output_dirname
  shutil.make_archive(folder + "_" + random , 'zip', output_dirname)
  
  zip_file = mode + "/" + folder + "_" + random + ".zip"


  


  return JsonResponse( 
        {
          "error" : error, 
          "filename" : imagepath , 
          "zip_path": zip_file, 
          "folder" : folder + "_" + random , 
          "mode" : mode 
          } )
    
 
def dbQuery(request):

  inputs = {}

  inputs["--query"] = request.POST['query']
  inputs["--input"] = request.POST['input']

  result = get_flags(inputs)

  return  JsonResponse( {"result" : result })
  

# Create your views here.
def makeGraph(inputs):
  return Make_Graphviz.createGraphBasedOnInput(inputs)


@csrf_exempt
def fileUpload(request):
    
  if request.method == 'POST':
    mode = request.POST.get("mode", "input")
    overwrite = request.POST.get("isOverwrite", False)
    
    #print("overwrite", overwrite )
    result = handle_uploaded_file( request.FILES['file'],  mode, overwrite)
    
    #if string is empty we have no errors hence success
    if not result :
      #fileList = loadFiles()
      #JsonResponse( {'success' : 'File uploading finished'} )

      return JsonResponse( {"data" : loadFiles(), 'mode' : mode })
      
    
    return JsonResponse({'error': result}, status = 403)

def handle_uploaded_file(f, mode, overwrite):
  import os.path
  
  
  fname = settings.UPLOADED_DIR  + f.name
  
  
  filename, file_extension = os.path.splitext(f.name)
  #print(fname)
  #print file_extension
  
  if file_extension != ".data" and file_extension != ".sqlite" and file_extension != ".dat" :
    return "Please select a valid file. Supported files are data and sqlite"
     
  
  if(os.path.isfile(fname) ):
    
    if int(overwrite) <> 0:
      #print("isOverwrite 2", overwrite )
      try:
        os.remove(fname)
      except OSError as e: # name the Exception `e`
        #print "Failed with:", e.strerror # look what it says
        #print "Error code:", e.code 
        return "File already exists and failed to overwrite. Reason is {0}. Please try again.".format(e.strerror)
    else: 
      #print("isOverwrite 3", overwrite )
      #print "Testing" + fname
      return "File already exists. Please rename and try to upload."
  
  with open(fname, 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
  
  return "";


def loadFileList(request):
  #mode = request.GET.get('mode','input')
  fileList = { "data" : loadFiles() }
  return JsonResponse(fileList)

def loadFiles():
  #print mode
  types = ('.data', '.sqlite', '.dat') # the tuple of file types
  
  return [each for each in os.listdir(settings.UPLOADED_DIR) if each.endswith(types)]
  


def loadCTList(request):
  mode = request.GET.get('mode','input')
  filename = request.GET.get('filename')
  listType = request.GET.get('type','')
  scenarioName = request.GET.get('scenario-name','')
  
  input = {"--input" : settings.UPLOADED_DIR + filename}
  
  if listType == 'commodity':
    input["--comm"] = True

  elif listType == 'technology':
    input["--tech"] = True

  elif listType == 'scenario':
    input["--scenario"] = True
  
  elif listType == 'period':
    input["--period"] = True  
    
  error = ''  
  data = {}
  
  try:
    data = get_comm_tech.get_info(input)
  except:
    error = 'An error occured. Please try again.'  
    
    #FIXME remove this when we get scenerios from tables
    #return JsonResponse( { "data" : {"Test1" : "Test1" , "Test2" : "Test2"} } )
  
 
  
  
  return JsonResponse( { "data" : data , "error" : error } )
