function get_predictor_word(special_word) {
	$.get("https://predictor.yandex.net/api/v1/predict.json/complete?key=pdct.1.1.20190520T131632Z.3bb85e2be86a334f.d62f8d9a13b6c3db36c06a86fd8a791860f62ce1&q=" + special_word + "&lang=ru&limit=3", function(data) {
    	if (data.text.length == 1) {
    		document.getElementById("predictor_word1").innerHTML = data.text[0];
    		document.getElementById("predictor_word2").innerHTML = '-'
    		document.getElementById("predictor_word3").innerHTML = '-'
    	}
    	else if (data.text.length == 2) {
    		document.getElementById("predictor_word1").innerHTML = data.text[0];
    		document.getElementById("predictor_word2").innerHTML = data.text[1];
    		document.getElementById("predictor_word3").innerHTML = '-'
    	}
    	else if (data.text.length == 3) {
    		document.getElementById("predictor_word1").innerHTML = data.text[0];
    		document.getElementById("predictor_word2").innerHTML = data.text[1];
    		document.getElementById("predictor_word3").innerHTML = data.text[2];
    	}
	});
}

$('#id_tags').on('input', function(e){
	var words = this.value.split(' ');
	var last_word = words[words.length - 1];
	get_predictor_word(last_word);
});

function add_predictor_word(number_of_word) {
	get_word = document.getElementById("predictor_word" + String(number_of_word)).innerHTML;
	input_value = document.getElementById("id_tags");
    var input_words = input_value.value.split(' ');
    var last_input_word = input_words[input_words.length - 1]
    if (get_word.includes(last_input_word)) {
        input_words[input_words.length - 1] = get_word;
        input_string = input_words.join(" ");
    } else {
        input_string = input_value.value + " " + get_word;
    }
	input_value.value = input_string;
	var words = input_value.value.split(' ');
	var last_word = words[words.length - 1];
	get_predictor_word(last_word)
}