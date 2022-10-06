departures = []


function myFunc(id, names) {
	for (x of names){
		var tag = document.createElement("option")
		var text = document.createTextNode(x);
		tag.appendChild(text);
		tag.value = x;
		var element = document.getElementById(id);
		element.appendChild(tag);
	}
}