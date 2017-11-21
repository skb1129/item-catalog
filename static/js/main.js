function loginCallback(authResult) {
	if (authResult['code']) {
		$.ajax({
			type: 'POST',
			url: '/gconnect?state={{STATE}}',
			processData: false,
			data: authResult['code'],
			contentType: 'application/octet-stream; charset=utf-8',
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


gapi.signin2.render('google_login', {
	'clientid': '328779283947-c2aqhd0qg0orkqunoc8ja2rb1mrq28or.apps.googleusercontent.com',
	'callback': loginCallback,
	'cookiepolicy': 'single_host_origin',
	'scope': 'openid email',
	'redirecturi': 'postmessage',
	'accesstype': 'offline',
	'approvalprompt': 'force'
});