// Get an array of the classes on the object.
function getClassList(element) {
    if (element.className && element.className != "") {
        return element.className.split(' ');
    }
    return [];
}

// Set the classes on an element from an array of class names
// Cache the list in the 'classes' attribute on the element
function setClassList(element, classlist) {
        element.className = classlist.join(' ');
}

// Determine the first index of a string in an array.
// Return -1 if the string is not found.
function indexOf(element, array) {
    if (!array || array.length == undefined) return -1;
    var i = array.length;
    while (i--) {
        if (array[i] == element) return i;
    }
    return -1;
}


// Remove the given class from an element, if it is there
function removeClass(element, classname) {
    var classes = getClassList(element);
    if (!classes) return;
    var index = indexOf(classname,classes);
    if (index >= 0) {
        classes.splice(index,1);
        setClassList(element, classes);
    }
}

// Add the given class to the element, unless it is already there
function addClass(element, classname) {
    var classes = getClassList(element);
    if (!classes) return;
    if (indexOf(classname, classes) < 0) {
        classes[classes.length] = classname;
        setClassList(element,classes);
    }
}

// Search box gets focus
function enableSearch(el) {
    if (!el.defaultValue) {
        el.defaultValue = el.value;
    }
    if (el.defaultValue == el.value) {
        el.value = "";
    }
    addClass(el, "focused");
}

// Search box loses focus
function disableSearch(el) {
    if (el.value == "" && el.defaultValue) el.value = el.defaultValue;
    removeClass(el, "focused");
}

