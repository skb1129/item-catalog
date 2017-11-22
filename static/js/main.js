function loginCallback(authResult) {
	if (authResult['code']) {
		$.ajax({
			type: 'POST',
			url: '/gconnect?state=' + state,
			processData: false,
			data: authResult['code'],
			contentType: 'application/json',
			success: function (result) {
				if (result) {
					window.location.href = '/';
				} else if (authResult['error']) {
					console.log('There was an error: ' + authResult['error']);
				} else {
					$('body').html('Failed to make a server-side call. Check your configuration and console.');
				}
			}
		});
	}
}

function logout() {
	$.ajax({
		type: 'POST',
		url: '/logout',
		processData: false,
		contentType: 'application/json',
		success: function (result) {
			if (result) {
				window.location.href = '/';
			} else {
				$('body').html('Failed to make a server-side call. Check your configuration and console.');
			}
		}
	});
}

gapi.signin.render('google_login', {
	'clientid': '328779283947-c2aqhd0qg0orkqunoc8ja2rb1mrq28or.apps.googleusercontent.com',
	'callback': loginCallback,
	'cookiepolicy': 'single_host_origin',
	'scope': 'openid email',
	'redirecturi': 'postmessage',
	'accesstype': 'offline',
	'approvalprompt': 'force'
});