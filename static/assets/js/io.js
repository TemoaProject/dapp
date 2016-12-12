function populateFileList(mode){
    var url = '/loadfilelist';

    $.ajax({
        url: url,
        dataType: 'json',
        method: 'get',
        data: {
            mode: mode
        },
        success: function(result) {

            var options = '<option value="0">--Select data File--</option>';
            $.each(result.data, function(index, obj) {
                options += "<option value=" + obj + ">" + obj + "</option>";
            });

            $("#datafilename").html(options);

        }
    });
}


function addTab(tabcontent)
{

    var id = $("#graphviz-tabs").children().length + 1; //think about it ;)


    var tabId = 'result_' + id;
    
    $("#graphviz-tabs").append('<li><a href="#result_' + id + '">Generated Result ' + id +'</a> <span> x </span></li>');
    
    $('#graphviz-content')
    .append('<div class="tab-pane" id="' + tabId + '"> ' + tabcontent + '</div>');
    
    $('#graphviz-tabs li:nth-child(' + id + ') a').click();
}



function displayNetworkDiagram(mode_folder, image_filename) {

    //file is inside result/ folder but due to static django we have to say url /static :(  ..enjoy :)
    var imgPath = "/static/" + mode_folder + "/" + image_filename + "?" + new Date().getTime(); ;
    
    var tabcontent = '<iframe class="result-frame" src="' + imgPath + '" width="800" alt="Output"></iframe> ';

    addTab(tabcontent);

    

   

    //$('#networkDiagram').html('<iframe class="result-frame" src="' + imgPath + '" width="800" alt="Output"></iframe> ');
}


function initForm(mode) {

    $('#commodity-technology-value').hide();
    $('#commodity-label').hide();
    $("#commodity-value-error").hide();
    $(".date-range").hide();
    
    
    $("#commodity-file-error").hide();
    $("#input-file-error").hide();
    $("#scenario-name-error").hide();
    $("#date-range-error").hide();

    var url = '/runinput';



    $("#input-form").submit(function(e) {


        e.preventDefault();

        $("#commodity-value-error").hide();

        var fileInput = $("#datafilename option:selected").text();
        if (fileInput == '--Select data File--' || fileInput == '')
        {
            $("#input-file-error").show();
            return false;
        }
        else
        {
            $("#input-file-error").hide();
        }


        //Only check if mode is output
        if(mode == "output")
        {
            var scenarioname = $("#scenario-name option:selected").text();
            if (scenarioname == '--Select scenario value--' || scenarioname == '')
            {
                $("#scenario-name-error").show();
                return false;
            }
            else
            {
                $("#scenario-name-error").hide();
            }
            
            
            var daterange = $("#date-range option:selected").text();
            if (daterange == '--Select period value--' || daterange == '')
            {
                $("#date-range-error").show();
                return false;
            }
            else
            {
                $("#date-range-error").hide();
            }
        }


        type = $('#commodity-technology-type').val();

        if(type != 'none')
        {
           filename = $("#commodity-technology-type").val();

            if(filename == '')
            {
                //alert("Select model first");
                $("#commodity-value-error").show();
                return;
            }
        }
        
        $(".spinner").removeClass("invisible");


        $.post( url, $('form#input-form').serialize(), function(data) {

            //alert(data.filename + data.mode);
            $(".spinner").addClass("invisible");
            
            if(data.error)
            {
                alert(data.error)
                return;
            }


            displayNetworkDiagram(data.mode, data.filename );

            //Make download button ready
            $("#download-button").addClass("btn-yellow").attr("href", "/static/" + data.zip_path);

        },
       'json' // I expect a JSON response
    );
});


/*
    fileInput = $("#file-list option:selected").text();
    if (fileInput == '--Select data File--') {
        $("#input-file-error").show();
        return false;
    } else {
        $("#input-file-error").hide();
    }
    comInput = $("#comomodity-input-text").val();
    comOutput = $("#comomodity-output-text").val();
    colorScheme = $("input[name=qcolorscheme]:checked").val();
    outputFormat = $("#output-format").text();
    displayNetworkDiagram();

    //alert("hi");


    $.ajax({
        url: url,
        method: "post",
        data: {datafile:fileInput,commodityoutputlimit:comInput,commodityinputlimit:comOutput,ccolorscheme:colorScheme,format:outputFormat},
        dataType: 'json',
        success: function(result) {
            alert(result);
            displayNetworkDiagram();
        }
    });*/

}

function showHideCommodityTechnology(mode){



    $('#commodity-technology-type').change(function(){

        type = $('#commodity-technology-type').val();

        if(type == 'none')
        {
            $('#commodity-technology-value').hide();
            $('#commodity-label').hide();
        }
        else
        {

            filename = $("#datafilename").val();

            if(filename == 0)
            {
                //alert("Select model first");
                $("#commodity-file-error").show();
                return;
            }

            $('#commodity-technology-value').show();
            $('#commodity-label').html("Select "+type+" value");
            $('#commodity-label').show();


            getCTList(mode, type, filename );
        }
    });
}

function getCTList(mode, type, filename){
    var url = '/loadctlist';

    $.ajax({
        url: url,
        dataType: 'json',
        method: 'get',
        data: {
            mode: mode,
            filename: filename,
            'type':type
        },
        success: function(result) {
            if(result.error)
            {
                alert(result.error)
                return;
            }
            
            if (type == "period")
            {
                result.data = result.data[$("#scenario-name").val()]
            }

            var options = '<option value="0">--Select '+ type +' value--</option>';
            $.each(result.data, function(index, obj) {
                options += "<option value=" + obj + ">" + obj + "</option>";
            });

			if(type == "scenario")
				$("#scenario-name").html(options);
         else if (type == "period")
        {
            $("#date-range").html(options); 
            $(".date-range").show();
        }
			else
            	$("#commodity-technology-value").html(options);

        }
    });
}

function showDownloadButtonWithHelp()
{
    $("#download-db").removeClass('hidden');
    $("#download-button-help").removeClass('hidden');
}

function initJs(mode)
{
    initForm(mode);

    

    populateFileList(mode);

    showHideCommodityTechnology(mode);



    $('#datafilename').change(function(){

        $('#commodity-technology-value').hide();
        $('#commodity-label').hide();

        $("#commodity-technology-type").val("none");
        $('#commodity-technology-value').html("");

        $("#commodity-file-error").hide();
        $("#input-file-error").hide();
        $("#scenario-name-error").hide();
        $("#date-range-error").hide();
        
        //showDownloadButtonWithHelp()


        if(mode == "output")
            getCTList(mode, "scenario", $(this).val() );

        //$("#download-db").attr("href", "/static/uploaded/files/" + this.value );
        

        console.log("DB changed!")

    });
    
    
    $('#scenario-name').change(function(){
        
        getCTList(mode, "period", $('#datafilename').val() );
    });


    // Dropzone class:
    var myDropzone = new Dropzone("div#dropArea", {
        url: "/fileupload",
        params: {
        mode: mode
    }
    });
    myDropzone.on('sending', function(file, xhr, formData){
            formData.append('isOverwrite', $("#isOverwrite").is(':checked') ? 1 : 0 );
    });

    myDropzone.on("success", function(fileList, response)
    {

        var options = '<option value="0">--Select Input File--</option>';

        $.each(response.data, function(index, obj) {
            options += fileList.name == obj ? "<option selected='selected' value=" + obj + ">" + obj + "</option>" :
                "<option value=" + obj + ">" + obj + "</option>";
        });

        $("#datafilename").html(options);

        myDropzone.removeAllFiles();
        
        //showDownloadButtonWithHelp();


        if(mode == "output")
            getCTList(mode, "scenario", fileList.name );

        showHideCommodityTechnology(mode);

    });






}




