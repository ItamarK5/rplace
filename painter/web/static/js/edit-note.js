const NoteTypeEnums = {
    limited_active: {row_color:'bg-success', text:'0'},
    limited_banned: {row_color:'table-warning', text:'1'},
    perment_active: {row_color:'table-success', text:'2'},
    perment_banned: {row_color:'table-danger', text:'3'},
    note : {row_color:'note'},
    /**
     * 
     * @param {Note object} note 
     */
    get_note_type(note) {
        if(!_.has(note, 'reason')){ // is info
            return this.info;
        } else if(this.expires == 'None'){
            return this.limited_active ? note.active : this.limited_banned;
        } // else:
        return this.limited_active ? note.active : this.limited_banned;
    }
}

const MakeNoteRow = (note) => {
    // note attributes needed:
    let note_row_type = NoteTypeEnums.get_note_type(note);
    let row = $('<tr></tr>').addClass(note_row_type);    
}

var notes = null;