/**
 * PostFormValidation - Form validation utilities for post creation
 */

export interface PostFormValues {
    text?: string;
    hasMedia?: boolean;
    selectedChannel?: string;
    scheduleTime?: string | Date | null;
}

export interface PostFormErrors {
    text?: string;
    selectedChannel?: string;
    scheduleTime?: string;
}

/**
 * Validates post form data and returns error messages
 * @param values - Form values to validate
 * @returns Validation errors object
 */
export const validatePostForm = (values: PostFormValues): PostFormErrors => {
    const errors: PostFormErrors = {};

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
 * @param formState - Current form state
 * @param formErrors - Form validation errors
 * @returns Whether form is valid for submission
 */
export const canSubmitForm = (formState: PostFormValues, formErrors: PostFormErrors): boolean => {
    const hasRequiredFields = Boolean(formState.text &&
                             formState.selectedChannel &&
                             formState.scheduleTime);

    const hasNoErrors = Object.keys(formErrors).length === 0;

    return hasRequiredFields && hasNoErrors;
};
