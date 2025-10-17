<!--Search-->
function change(category, value_change, text_change)
{
  var button_elem = document.getElementById(category);
  var input_elem = document.getElementById('i'+category);
  input_elem.value = value_change;
  console.log(value_change, input_elem.value)
  if (!text_change)
    button_elem.innerHTML = category;
  else
    button_elem.innerHTML = text_change
}

<!--Profile Rating-->
function change_rating(num)
{
    var rating = document.getElementById("rating_value")
    rating.value = num;
    var elem = document.getElementById("rate"+num)
    for(let i=1; i<=num; i++){
         elem = document.getElementById("rate"+i)
         elem.value = "🌕";
    }
    var elem = document.getElementById("rate"+num)
    if (elem.value == "🌕"){
        for(let i=1; i<=5; i++){
            elem = document.getElementById("rate"+i)
            if (i>num) elem.value = "🌑";
            else elem.value = "🌕";
        }
    }
}

<!--Profile Edit-->
function add(){
    var input_box_no = parseInt($('#total_inputs').val())+1;
    var new_input1="<input type='text' class='form-control mt-2 mb-1 col' placeholder='Social Media Name'  id='social"+input_box_no+"' required>";
    var new_input2="<input type='text' class='form-control mt-2 mb-1 col' placeholder='@Username'  id='username"+input_box_no+"' required>";
    var new_div="<div id='div_"+input_box_no+"' class='d-flex flex-row'></div>";

    $('#input_box').append(new_div);

    $('#div_'+input_box_no).append(new_input1, new_input2);
    $('#total_inputs').val(input_box_no)
}
function remove(){
    var last_input_no = $('#total_inputs').val();
    if(last_input_no>1){
      $('#div_'+last_input_no).remove();
      $('#total_inputs').val(last_input_no-1);
    }
}
function save(){
    var last_input_no = $('#total_inputs').val();
    var contact = document.getElementById("contact")
    if ($('#social').val() && $('#username').val())
      contact.value = $('#social').val() + ':' + $('#username').val() + '|';
      if(last_input_no>1){
        for(i=1; i<last_input_no; i++){
          contact.value += $('#social'+(i+1)).val() + ':';
          contact.value += $('#username'+(i+1)).val() + '|';
        }
    }
    console.log(contact.value, 'Final')
}