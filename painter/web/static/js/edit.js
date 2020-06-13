/**
 * @auther Itamar Kanne
 * @file this file includes all javascript code that runs in the edit user page.
 */

/** @const history_table jquery reference */
const history_table = $('#history-table');
// map for note type
/** 
 * @constant {Object.<string, Object.<string, string>>} NoteTypeEnums
 * @enum {Object.<string, string>}
 * options for different type of 
 */
const NoteTypeEnums = {
	unbanned_date: {row_class:'primary', text:'Future Unbanned Record'},
	banned_date: {row_class:'warning', text:'Future Banned Record'},
	unbanned: {row_class:'success', text:'Active Record'},
	banned: {row_class:'danger', text:'Banned Record'},
	note : {row_class:'info', text:'Note Record'},
}


class Note {
	/**
	 * @param {number} id the id of the note
	 * @param {string} post_date the date the note was created
	 * @param {string} type type of the row @see {@link NoteTypeEnums}
	 * @param {string} writer the name of the writer of the note
	 * @param {string} description the text of note, what was written there
	 * @param {boolean} can_edit if user has permission to edit the note
	 * @param {?string} affect_form the date the note taken effect (if its record), if its a simple note its value is null
	 * @param {?string} reason message to the user why he was banned (if its record), if its a simple note its value is null
	 * @param {?boolean} active if the user was active after the note taken effect (if its record), if its a simple note its value is null
	 */
	constructor(id, type, post_date, writer, description, can_edit,
		affect_from, reason, active){
			this.id = id;
			this.type = type;
			this.post_date = post_date;
			this.writer = writer;
			this.description = description;
			this.can_edit = can_edit
			this.affect_from = affect_from;
			this.reason = reason;
			this.active = active;
	}
}

// get the user name from the url (that suppose to be)
/**
 * @function
 * @name GetUserName
 * @returns {string} name of the user in url
 * gets the user name
 * url build in as http://127.0.0.1:8080/edit-user/{name}
 */
const GetUserName = () => window.location.pathname.split('/')[2];
/**
 * @function
 * @name GetTargetRow
 * @returns the current selected row of history rows [the one targeted]
 * get a targeted note row in historyModal
 */
const GetTargetRow = () => $('tr[targeted="true"]');


/**
 * @function
 * @name MakeNoteRow 
 * @param {Note} note note object
 */
const MakeNoteRow = (note) => {
	// note attributes needed:
	console.log(note)
	let note_row_type = NoteTypeEnums[note.type];
	let row = $('<tr></tr>')
				.addClass('table-' + note_row_type.row_class)
				.addClass('note-history-row')
				.attr({
					'data-item': note.id,
				});
	row.append($('<td></td>').text(note.post_date));
	row.append($('<td></td>').text(note.writer));
	row.append($('<td></td>').text(note_row_type.text));
	return row;
}


/**
 * @name hasNotFoundResponse
 * @param {XMLHttpRequest} xhr 
 * @return {Boolean} if its a 404 response (not found)
 * checks if response is XMLHttpResponse with status 404
 */
const hasNotFoundResponse = (xhr) => _.has(xhr, 'status') && xhr.status == 404;

/**
 * @param {?number|?string}} num represent the number of the page
 * @param {?string} text text of he number
 * @returns {HTMLButtonElement} new button
 * create page button from page data
 */
function makePageButton(num, text=null){
	// determine null text
	if(_.isNull(text)){
		text = _.isNull(num) ? 'none' : num.toString() 
	}
	// create page button
	let is_disabled =  _.isNull(num) || isNaN(num);
	let button = $('<button></button>').attr({
		type:'button',
		href: is_disabled ? 'none' : num.toString()
	}).text(text).addClass('btn btn-secondary page-button');
	if(is_disabled){
		// add disabled
		button.addClass('disabled')
	}
	return button
}

/**
 * @param {JSON} json_data
 * @returns {Note} new note
 * transfers note in json to note object
 */
const ConvertJSONToNotes = (json_data) =>{
	return new Note(
		json_data.id,
		json_data.type,
		json_data.post_date,
		json_data.writer,
		json_data.description,
		json_data.can_edit,
		_.has(json_data, 'affect_from') ? json_data.affect_from : null ,
		_.has(json_data, 'reason') ? json_data.reason : null ,
		_.has(json_data, 'active') ? json_data.reason : null
	)
}



/**
 * @function
 * @param {jQuery} note_row selector for a row that describes a note
 * sets it color to focus bg-{state} -> table-{state}
 */
const FocusNoteRow = (note_row) => {
	let row_class = NoteTypeEnums[notes.getNoteOfRow(note_row).type].row_class
	$(note_row).addClass(`bg-${row_class}`);
	$(note_row).removeClass(`table-${row_class}`);
}

/**
 * @function
 * @param {jQuery} note_row selector for a row that describes a note
 *  focus a note row, sets its background to bg type background
 * sets it color to focus bg-{state} -> table-{state}
 */
const LoseFocusNoteRow = (note_row) => {
	let row_class = NoteTypeEnums[notes.getNoteOfRow(note_row).type].row_class
	$(note_row).addClass(`table-${row_class}`);
	$(note_row).removeClass(`bg-${row_class}`);
}


/**
 * 
 * @param {Note} note a specific not
 * describes the note on the fields
 */
function ShowNoteDetails(note){
	// note, if note is false like null or undefined, sets undefined.
	note = Boolean(note) ? note : new Note(-1, '', '', '', '', '')
	if(note.type == 'note'){
		$('.record-row:not(.d-none)').addClass('d-none')
	} else {
		$('.record-row.d-none').removeClass('d-none');
	}
	// sets field texts
	$('#post-date-field').val(note.post_date);
	$('#writer-field').val(note.writer);
	$('#description-field').text(note.description)
	if(note.type != 'note'){
		$('#affect-from-field').val(_.isNull(note.affect_from) ? note.post_date : note.affect_from);	// if the date was from the same time
		$('#active-field').val(note.active);
		$('#reason-field').text(note.reason);
	} else {
		$('#reason-field').text('')
		$('#affect-from-field').text('')
		$('#active-field').text('')
	}
	if(note.can_edit){
		$('#edit-note-tools').removeClass('d-none');
		$('#description-field').prop('disabled', false);
	} else {
		$('#edit-note-tools').addClass('d-none');
		$('#description-field').prop('disabled', true);
	}
	$('#edit-note-button').prop('disabled', true)
}

/** 
 * @namespace notes 
 * @property {?number[]} pages
 * @property {?number} prev_ref previous page reference, number of the page but if there isn't a prev page then null
 * @property {?number} next_ref next page reference, number of the page but if there isn't a next page then null
 * @property {?number} current_page current page displayed, if there isn't any returns null
 * @property {Note[]} query query of notes 
 * @property {Note} __selected_note the current selected note
*/
const notes = {
	pages:null,
	prev_ref:null,
	next_ref:null,
	current_page:null,
	__selected_note:null,
	query:null,
	/**
	 * @returns the current selected note
	 * simple get method
	 */
	get selected_note() {
		return this.__selected_note;
	},
	/**
	 * @param {*} value a new note that is being selected
	 * simple set method and update handle function
	 */
	set selected_note(value){
		if(value != this.__selected_note){
			this.__selected_note = value;  
			// show note details 
			ShowNoteDetails(value);
		}
	},
	/**
	 * 
	 * @param {jQuery} row_selector of a note
	 * @returns {undefined|Note} note or undefined 
	 */
	getNoteOfRow(row_selector) {
		return this.query[
			_.findIndex(
				this.query, 
				(note) => note.id == parseInt($(row_selector).attr('data-item'))
			)
		];
	},
	/**
	 * recreates all notes on DOM and page buttons
	 */
	updateNotes(){
		console.log(this.query)
		this.makeHistory()
		this.makePages()
	},
	/** 
	 * make all rows of notes 
	*/
	makeHistory(){
		history_table.children('tr').remove();
		this.query.forEach((value) => {
			history_table.append(MakeNoteRow(value))
		});
		// events
		$('.note-history-row').hover(
			//hover
			function() {
				FocusNoteRow(this)
			},
			//unhoer
			function(){
				console.log($(this).attr('targeted'))
				if($(this).attr('targeted') != 'true'){
					LoseFocusNoteRow(this);	 
				}
			}
		)
		$('.note-history-row').click(function() {
			let data_item = $(this).attr('data-item');
			$('tr[targeted="true"]').each(function() {
				// this referenced to the current targeted row
				if($(this).attr('data-item') != data_item){
					$(this).attr('targeted', "false");
					LoseFocusNoteRow(this);
				}
			})
			$(this).attr('targeted', "true");
			FocusNoteRow(this);
			// set note as selected if clicked
			notes.selected_note = notes.getNoteOfRow(this);
		})
	},
	/**
	 * creates all page references buttons
	 */
	makePages(){
		let page_group = $('#page-group');
		$('.page-button').remove();
		page_group.append(makePageButton(this.prev_ref, 'Prev'));
		this.pages.forEach((val) => {
			if(_.isNull(val)){
				val = '...'
			}
			let button = makePageButton(val);
			console.log(val, this.current_page)
			if(val == this.current_page){
				button.addClass('active')
			}
			page_group.append(button)
		})
		page_group.append(makePageButton(this.next_ref, 'Next'));
		$('.page-button').click(function(e) {
			if($(this).hasClass('disabled')){
				e.preventDefault();
				Swal.fire({
					icon:'error',
					title:'Cannot access page'
				})
			} else if($(this).hasClass('active')){
				e.preventDefault()
			} else {
				let href = parseInt(this.getAttribute('href'));
				AjaxGetPage(isNaN(href) ? 0 : href)
			}
		});
	},
	/**
	 * @param {number} remove_note_id 
	 */
	removeNote(remove_note_id){
		this.notes = _.filter(this.notes, (note) => note.id != remove_note_id)
		$(`.note-history-row[data-item="${remove_note_id}"]`).remove();
		if(this.selected_note.id == remove_note_id){
			this.selected_note = null;   // clears the display note column
		}

	}
};


/**
 * @function
 * ajaxErrorAlert
 * @param {error} error error response of the ajax request
 * @param {?function} result_func function to apply after closed the alert
 * show a pop up message for the error and then executes an options function (result_func)
 */
function ajaxErrorAlert(error, result_func) {
	let alert = Swal.fire({
		title: 'Error!',
		icon: 'error',
		html: error.responseText,
		showCanelButton: _.isFunction(result_func)
	})
	if(result_func){
		alert.then((result) => result_func(result, error))
	}
}

// get page by ajax request
/**
 * @param {number} page page to get
 * @returns nothing
 * gets the current page by ajax request
 */
function AjaxGetPage(page=1){
	return $.get({
		url:'/get-notes',
		data: {name:GetUserName(), page:page}, 
		contentType: 'application/json;charset=UTF-8',
		success: (data) => {
			console.log(data)
			notes.pages=data.pages;
			notes.query= _.map(
				data.query,
				ConvertJSONToNotes
			)
			notes.prev_ref=data.prev_ref;
			notes.next_ref=data.next_ref;
			notes.current_page=data.current_page;
			notes.updateNotes()
		},
		error:ajaxErrorAlert
	}).catch(() => {
		ajaxErrorAlert({responseText:'fail-to-get-message'})
	});
}

// serialize form
// add serializeForm
/**
 * @method serializeForm
 * serialize a form, returns dictionary of all fields fromserialize array
 * 
 */
//@ts-ignore
$.fn.serializeForm = function() {
	var output = { csrf_token : csrf_token };
	var fields_array = this.serializeArray();
	// check each object in the array
	$.each(fields_array, function() {
		if (output[this.name]) {
			if (!output[this.name].push) {
				output[this.name] = [output[this.name]];
			}
			output[this.name].push(this.value || '');
		} else {
			output[this.name] = this.value || '';
		}
	});
	return output;
};

// run when ready, when its safe to edit html elements 
$(document).ready(() => {
	$('[data-toggle="tooltip"]').tooltip()
	// when display history modal
	$('#historyModal').on('show.bs.modal', (e) => {
		// no page
		if(notes.current_page == null){
			e.stopPropagation();
			Swal.fire({
				icon:'warning',
				title:'Didnt gain history',
				text:'Cant load notes history from server, pless wait until it loads'
			})
	
		}
	})
	// get pages
	AjaxGetPage();
	$('#record-form').submit(function(e) {
		let success_message = $('#record-form .success-message')[0];
		if (!success_message.hasAttribute('hidden')) {
			success_message.toggleAttribute('hidden');
		}
		$('.error-list').children().remove();
		e.preventDefault();
		let args = $(this).serializeForm();
		// post request
		$.post({
			url:$(this).attr('action'),
			data:JSON.stringify(args),
			contentType: "application/json;charset=utf-8",
			success: (data) => {
				console.log(data, typeof(data))
			   if (data.valid) {
					success_message.removeAttribute('hidden')
				} else {
					// need to work for csrf error
					_.pairs(data.errors).forEach(function(row){
						let field = row[0];
						let errors = row[1];
						console.log(field, errors);
						errors.forEach(function(err){
							$('<ul></ul>')
							.text(err)
							.addClass("center-text list-group-item list-group-item-danger")
							.appendTo($(`#record-form .error-list[error-for="${field}"]`).first())
						})
					})
				}
			},
		}).catch(ajaxErrorAlert)
	});
	$('#note-form').submit(function(e) {
		let success_message = $('#note-form .success-message')[0];
		if (!success_message.hasAttribute('hidden')) {
			success_message.toggleAttribute('hidden');
		}
		//@ts-ignore
		let args = $(this).serializeForm();
		$('#note-form .error-list').children().remove();
		e.preventDefault();
		$.post({
			url:$(this).attr('action'),
			data:JSON.stringify(args),
			contentType: "application/json;charset=utf-8",
			success: (data) => {
				if (data.valid) {
					success_message.removeAttribute('hidden')
				} else {
					// need to work for csrf error
					_.pairs(data.errors).forEach(function(row){
						let field = row[0];
						row[1].forEach(function(err){
							$('<ul></ul>')
							.text(err)
							.addClass("center-text list-group-item list-group-item-danger")
							.appendTo($(`#note-form .error-list[error-for="${field}"]`).first())
						})
					})
				}
			}
		}).fail(ajaxErrorAlert);
	});
	// forms submitted
	$('#submit-note-form').click(() => {
		$('#note-form').submit();
	})
	
	$('#submit-record-form').click(() => {
		$('#record-form').submit();
	})
	// affect from field in historyModal
	$('#set-affect-from').click(function() {
		let field = $('#affect_from')[0];
		if (this.checked) {
			field.removeAttribute('disabled');
		} else {
			field.setAttribute('disabled', 'disabled')
		}
	})
	// change rank button
	$('#rank-button').click(function() {
		let name = this.getAttribute('enum-name');
		Swal.fire({
			title: 'Are you sure?',
			text: `You want to set this user's rank to ${name}`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Yes Set Rank!'
		}).then((result) => {
			if (result.value) {
				$.ajax({
					url: `/set-user-role/${GetUserName()}`,
					method: 'POST',
					contentType: 'application/json;charset=UTF-8',
					data: name,
					// success message
					success: function(data) {
						Swal.fire({
							title: data.success ? 'Role Changed' : 'Error!',
							icon: data.success ? 'success' : 'error',
							text: data.text
						});
					},
					// error message
					error: ajaxErrorAlert
				})
			}
		})
	});
	$('#refresh-history').click(function(){
		$(this).text('')
		$(this).append(
			$('<div></div>')
			.addClass('text-secondary spinner-border')
			.append($('<span></span>')
			.addClass('sr-only')
			.text('Loading'))
		)
		AjaxGetPage(notes.current_page).then(() => {
			$('#refresh-history').children('div').remove();
			$('#refresh-history').text('refresh');
		})
	});
	$('#remove-note-button').click(() => {
		let targeted_row = GetTargetRow();
		let note_idx = parseInt(targeted_row.attr('data-item'))
		if(targeted_row){
			$.post({
				url:`/delete-note`,
				data:JSON.stringify(note_idx),
				contentType: 'application/json;charset=UTF-8',
				success: (response) => {
					if(response.success){
						Swal.fire({
							icon:'success',
							text:'Success',
							error:response.text
						})
					}
					notes.removeNote(note_idx)
				},
			}).catch((error) => {
				if(hasNotFoundResponse(error)){
					// then the note isnt found so it must have been deleted
					notes.removeNote(note_id)
				}
				ajaxErrorAlert(error)
			})
		}
	})
	$('#description-field').on('input', function(e) {
		console.log(notes.selected_note)
		if(notes.selected_note){
			$('#edit-note-button').prop('disabled', $(this).val() == notes.selected_note.description)
		}
	})
	$('#edit-note-button').click(() => {
		if(notes.selected_note.can_edit){
			let note_id = notes.selected_note.id
			$.post({
				url:'/change-note-description',
				data: JSON.stringify({
					id:notes.selected_note.id,
					description:$('#description-field').text()
				}),
				contentType: 'application/json;charset=UTF-8',
				success(response) {
					console.log(text)
					Swal.alert({
						icon:'success',
						title:'success',
						text:text
					})
				}
			}).catch(error => {
				//throw ajax alert
				if(hasNotFoundResponse(error)){
					notes.removeNote(note_id)
				}
				ajaxErrorAlert(error);
			})
		}
	})

})

/** 
 * on windows load
 * serialize the date input
 */
$(window).on('load', function() {
	$('#affect_from').datetimepicker({
		format: 'DD/MM/YYYY HH:mm',
		showTodayButton: true,
		showClear: true,
		showClose: true,
		icons: {
			// icons
			time: 'far fa-clock', // to select time
			date: 'fas fa-calendar', // to select date
			up: 'fas fa-arrow-up',  // move time up
			down: 'fas fa-arrow-down', // move time down
			previous: 'fas fa-chevron-left', // get previous day
			next: 'fas fa-chevron-right', // get next day
			today: 'fas fa-calendar-check-o',   // sets today
			clear: 'fas fa-trash',  // clear the time
			close: 'fas fa-times' // close tme
		},
		// time zone
		timeZone: 'utc-0'
	})
});