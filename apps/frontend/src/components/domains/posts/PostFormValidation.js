/**
 * PostFormValidation - Form validation utilities for post creation
 */

/**
 * Validates post form data and returns error messages
 * @param {Object} values - Form values to validate
 * @returns {Object} - Validation errors object
 */
export const validatePostForm = (values) => {
    const errors = {};
    
    if (!values.text?.trim() && !values.hasMedia) {
        errors.text = 'Please add some text or upload an image to create your post';
    }
    
    if (values.text && values.text.length > 4096) {
        errors.text = `Your message is too long (${values.text.length}/4096 characters). Please shorten it.`;
    }
    
    if (!values.selectedChannel) {
        errors.selectedChannel = 'Please select a channel to post to';
    }
    
    if (!values.scheduleTime) {
        errors.scheduleTime = 'Please select when you want to publish this post';
    } else if (new Date(values.scheduleTime) <= new Date()) {
        errors.scheduleTime = 'Please choose a time in the future for scheduling';
    }
    
    return errors;
};

/**
 * Determines if form can be submitted based on validation
 * @param {Object} formState - Current form state
 * @param {Object} formErrors - Form validation errors
 * @returns {boolean} - Whether form is valid for submission
 */
export const canSubmitForm = (formState, formErrors) => {
    const hasRequiredFields = (formState.text?.trim() || formState.hasMedia) &&
                             formState.selectedChannel &&
                             formState.scheduleTime;
    
    const hasNoErrors = Object.keys(formErrors).length === 0;
    
    return hasRequiredFields && hasNoErrors;
};