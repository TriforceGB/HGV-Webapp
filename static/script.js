
function confirmClearForm(){
    var result = window.confirm("Are you sure you want to clear the form?");
    if(result){
        document.getElementById("report-form").reset();
    } 
}

  fetch('/header')
    .then(response => response.text())
    .then(data => document.getElementById('header').innerHTML = data)
