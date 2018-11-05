/**
 * This is an example of a basic node.js script that performs
 * the Authorization Code oAuth2 flow to authenticate against
 * the Spotify Accounts.
 *
 * For more information, read
 * https://developer.spotify.com/web-api/authorization-guide/#authorization_code_flow
 */

var express = require('express'); // Express web server framework
var request = require('request'); // "Request" library
var cors = require('cors');
var querystring = require('querystring');
var cookieParser = require('cookie-parser');
var SpotifyWebApi = require('spotify-web-api-node');


var client_id = '9f409b4e7b7d4e589b13fe8a0ada6f23'; // Your client id
var client_secret = 'd4c48893bbcf4fdd8d0a37c67402213b'; // Your secret
var redirect_uri = 'http://localhost:8888/callback'; // Your redirect uri

var spotifyApi = new SpotifyWebApi({
	clientId: client_id,
	clientSecret: client_secret,
	redirectUri: redirect_uri
});

/**
 * Generates a random string containing numbers and letters
 * @param  {number} length The length of the string
 * @return {string} The generated string
 */
var generateRandomString = function(length)
{
	var text = '';
	var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

	for (var i = 0; i < length; i++)
	{
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
};

var stateKey = 'spotify_auth_state';

var app = express();

app.use(express.static(__dirname + '/public'))
	.use(cors())
	.use(cookieParser());

app.get('/login', function(req, res)
{

	var state = generateRandomString(16);
	res.cookie(stateKey, state);

	// your application requests authorization
	var scope = 'user-read-private user-read-email';
	res.redirect('https://accounts.spotify.com/authorize?' +
		querystring.stringify({
			response_type: 'code',
			client_id: client_id,
			scope: scope,
			redirect_uri: redirect_uri,
			state: state
		}));
});

app.get('/callback', function(req, res)
{

	// your application requests refresh and access tokens
	// after checking the state parameter

	var code = req.query.code || null;
	var state = req.query.state || null;
	var storedState = req.cookies ? req.cookies[stateKey] : null;

	if (state === null || state !== storedState)
	{
		res.redirect('/#' +
			querystring.stringify({
				error: 'state_mismatch'
			}));
	} else
	{
		res.clearCookie(stateKey);
		var authOptions = {
			url: 'https://accounts.spotify.com/api/token',
			form: {
				code: code,
				redirect_uri: redirect_uri,
				grant_type: 'authorization_code'
			},
			headers: {
				'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))
			},
			json: true
		};

		request.post(authOptions, function(error, response, body)
		{
			if (!error && response.statusCode === 200)
			{

				var access_token = body.access_token,
					refresh_token = body.refresh_token;

				var options = {
					url: 'https://api.spotify.com/v1/me',
					headers: {'Authorization': 'Bearer ' + access_token},
					json: true
				};

				// use the access token to access the Spotify Web API
				request.get(options, function(error, response, body)
				{
					console.log(body);
				});

				spotifyApi.setAccessToken(access_token);

				var fs = require('fs');
				var CsvReadableStream = require('csv-reader');

				var inputStream = fs.createReadStream('billboardLC.csv', 'utf8');

				inputStream
					.pipe(CsvReadableStream({parseNumbers: true, parseBooleans: true, trim: true}))
					.on('data', function(row)
					{
						console.log('song: ' + row[1]);
						console.log('artist: ' + row[2]);
						var wait = false;
						spotifyApi.searchTracks(row[1], {limit: 1}).then(function(val)
						{
							console.log(val.body.tracks.items[0].id);
							console.log(val.body.tracks.items[0].name);
							console.log(val.body.tracks.items[0].artists[0].name);
							wait = true;

						},
							function(err)
							{
								console.error(err);
								wait = true;
							});
					})
					.on('end', function(data)
					{
						console.log('No more rows!');
					});




				// we can also pass the token to the browser to make requests from there
				res.redirect('/#' +
					querystring.stringify({
						access_token: access_token,
						refresh_token: refresh_token
					}));
			} else
			{
				res.redirect('/#' +
					querystring.stringify({
						error: 'invalid_token'
					}));
			}
		});
	}
});

app.get('/refresh_token', function(req, res)
{

	// requesting access token from refresh token
	var refresh_token = req.query.refresh_token;
	var authOptions = {
		url: 'https://accounts.spotify.com/api/token',
		headers: {'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64'))},
		form: {
			grant_type: 'refresh_token',
			refresh_token: refresh_token
		},
		json: true
	};

	request.post(authOptions, function(error, response, body)
	{
		if (!error && response.statusCode === 200)
		{
			var access_token = body.access_token;
			res.send({
				'access_token': access_token
			});
		}
	});
});

function sleep(milliseconds)
{
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++)
	{
		if ((new Date().getTime() - start) > milliseconds)
		{
			break;
		}
	}
}

console.log('Listening on 8888');
app.listen(8888);
