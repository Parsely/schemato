var status_string;
var status_url;
var didFinishValidating = true;
var intval;

function buildError(data, classname){
    var error = $("<div />").addClass(classname);
    var line = $("<p />").addClass("line-no");
    line.append("Line " + data.num + ": ");
    line.append($("<code />").append(data.line))
    var msg = $("<p />").append(data.string);
    error.append(line);
    error.append(msg);
    return error;
}

function appendResult(result){
    if(result.warnings.length > 0 || result.errors.length > 0){
        $('#result').append($("<p />").text(result.namespace));

        var canonical_errors = [];
        $.each(result.errors, function(key, value){
            console.log(value);
            if(canonical_errors.indexOf(value.string) == -1){
                canonical_errors.push(value.string);
                var error = buildError(value, "error");
                $("#result").append(error);
            }
        });

        var canonical_warnings = [];
        $.each(result.warnings, function(key, value){
            if(canonical_warnings.indexOf(value.string) == -1){
                canonical_warnings.push(value.string);
                var warn = buildError(value, "warning");
                $("#result").append(warn);
            }
        });
    } else {
        $("#result").append("No errors found!");
    }
}

function storeResults(data){
    url = ontology = errors = ont_name = msg = undefined;
    didFinishValidating = true;
    $("#working").empty();
    $.each(data, function(key, value){
        appendResult(value);
    });
}

function getStatus(){
    $.getJSON(status_url, function(response){
        if(response.status == 'WORKING'){
            $("#working").html("<p style='text-align: center;'>Validating...<br /><img src='static/img/loading.gif' /></p>");
        } else {
            clearInterval(intval);
            storeResults(response.data);
        }
    });
}

function postData(){
    $("#linkform").submit(function(e){
        e.preventDefault();
        $("#result").empty();
        if(didFinishValidating){
            $.post("/validate", $("#linkform").serialize(),
            function(data){
                status_url = data.url;
            }, "json");
            didFinishValidating = false;
        }
    });
    intval = setInterval('getStatus()', 500);
}
