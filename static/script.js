console.log("JS loaded");

document.getElementById("form").addEventListener("submit", function(e){

e.preventDefault();

console.log("Form submitted");

let data = {
name: document.getElementById("name").value,
email: document.getElementById("email").value,
phone: document.getElementById("phone").value,
location: document.getElementById("location").value
};

fetch("/book",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify(data)
})

.then(res=>res.json())

.then(result=>{
document.getElementById("message").innerText=result.message;
})

.catch(err=>console.log(err));

});