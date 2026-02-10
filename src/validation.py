def validation(result,shadow_out_csv):
    from validate.getData import process_mission_data,parse_shadow_ranges
    from validate.validate import call_validate
    col_list_for_validation, com_list_for_validation, proc_list_for_validation = process_mission_data(result)
    shadow_list_for_validation = parse_shadow_ranges(shadow_out_csv)
    call_validate(col_list_for_validation, com_list_for_validation, proc_list_for_validation,shadow_list_for_validation )
