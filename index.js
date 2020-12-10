tags = document.getElementsByClassName("tag");
for (var i=0; i<tags.length; i++) {
  tags[i].addEventListener('click', changeDisplay, false);
}
blogs = document.getElementsByClassName("link-a");

document.getElementById('All').style.backgroundColor = '#6c757d';
document.getElementById('All').style.color = 'white';

function changeDisplay(e){
  id = e['currentTarget']['id'];
  for (var i=0; i<tags.length; i++) {
    tags[i].style.backgroundColor = '#f4f4f4';
	tags[i].style.color = 'black';
  }
  document.getElementById(id).style.backgroundColor = '#6c757d';
  document.getElementById(id).style.color = 'white';
  if (id=="All") {
    for (var i=0; i<blogs.length; i++) {
	  blogs[i].style.display = 'inline';
	}
  }
  else {
    for (var i=0; i<blogs.length; i++) {
	  if (blogs[i].getAttribute('data-tag').includes(id)) {
	    blogs[i].style.display = 'inline';
	  }
	  else {
	    blogs[i].style.display = 'none';
	  }
	}
  }
}
