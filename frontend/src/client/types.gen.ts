// This file is auto-generated by @hey-api/openapi-ts

export type BeginLabourRequest = {
    first_labour: boolean;
};

export type BirthingPersonDTO = {
    id: string;
    first_name: string;
    last_name: string;
    labours: Array<LabourDTO>;
    subscribers: Array<(string)>;
};

export type BirthingPersonResponse = {
    birthing_person: BirthingPersonDTO;
};

export type BirthingPersonSubscriptionTokenResponse = {
    token: string;
};

export type BirthingPersonSummaryDTO = {
    id: string;
    first_name: string;
    last_name: string;
    active_labour: (LabourSummaryDTO | null);
};

export type BirthingPersonSummaryResponse = {
    birthing_person: BirthingPersonSummaryDTO;
};

export type Body_login_api_v1_auth_login_post = {
    username: string;
    password: string;
};

export type CompleteLabourRequest = {
    end_time?: (string | null);
    notes?: (string | null);
};

export type ContractionDTO = {
    id: string;
    labour_id: string;
    start_time: string;
    end_time: string;
    duration: number;
    intensity: (number | null);
    notes: (string | null);
    is_active: boolean;
};

export type EndContractionRequest = {
    intensity: number;
    end_time?: (string | null);
    notes?: (string | null);
};

export type ExceptionSchema = {
    description: string;
};

export type GetSubscriptionsResponse = {
    subscriptions: Array<BirthingPersonSummaryDTO>;
};

export type HTTPValidationError = {
    detail?: Array<ValidationError>;
};

export type LabourDTO = {
    id: string;
    birthing_person_id: string;
    start_time: string;
    end_time: (string | null);
    current_phase: string;
    notes: (string | null);
    contractions: Array<ContractionDTO>;
    pattern: (LabourPatternDTO | null);
};

export type LabourPatternDTO = {
    average_duration_minutes: number;
    average_intensity: number;
    average_interval_minutes: number;
    phase: string;
};

export type LabourResponse = {
    labour: LabourDTO;
};

export type LabourSummaryDTO = {
    id: string;
    duration: number;
    contraction_count: number;
    current_phase: string;
    hospital_recommended: boolean;
    pattern: (LabourPatternDTO | null);
};

export type LabourSummaryResponse = {
    labour: LabourSummaryDTO;
};

export type RegisterSubscriberRequest = {
    contact_methods: Array<(string)>;
};

export type StartContractionRequest = {
    intensity?: (number | null);
    start_time?: (string | null);
    notes?: (string | null);
};

export type SubscriberDTO = {
    id: string;
    first_name: string;
    last_name: string;
    phone_number: (string | null);
    email: (string | null);
    contact_methods: Array<(string)>;
    subscribed_to: Array<(string)>;
};

export type SubscriberResponse = {
    subscriber: SubscriberDTO;
};

export type SubscribeToRequest = {
    token: string;
};

export type TokenResponse = {
    access_token: string;
    token_type?: string;
};

export type UnsubscribeFromRequest = {
    birthing_person_id: string;
};

export type User = {
    id: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number?: (string | null);
};

export type ValidationError = {
    loc: Array<(string | number)>;
    msg: string;
    type: string;
};

export type LoginApiV1AuthLoginPostData = {
    formData: Body_login_api_v1_auth_login_post;
};

export type LoginApiV1AuthLoginPostResponse = (TokenResponse);

export type GetUserApiV1AuthUserGetResponse = (User);

export type RegisterApiV1BirthingPersonRegisterPostResponse = (BirthingPersonResponse);

export type GetBirthingPersonApiV1BirthingPersonGetResponse = (BirthingPersonResponse);

export type GetBirthingPersonSummaryApiV1BirthingPersonSummaryGetResponse = (BirthingPersonSummaryResponse);

export type GetSubscriptionTokenApiV1BirthingPersonSubscriptionTokenGetResponse = (BirthingPersonSubscriptionTokenResponse);

export type RedirectToDocsGetResponse = (unknown);

export type HealthcheckApiV1HealthGetResponse = ({
    [key: string]: (string);
});

export type BeginLabourApiV1LabourBeginPostData = {
    requestBody: BeginLabourRequest;
};

export type BeginLabourApiV1LabourBeginPostResponse = (LabourResponse);

export type StartContractionApiV1LabourContractionStartPostData = {
    requestBody: StartContractionRequest;
};

export type StartContractionApiV1LabourContractionStartPostResponse = (LabourResponse);

export type EndContractionApiV1LabourContractionEndPutData = {
    requestBody: EndContractionRequest;
};

export type EndContractionApiV1LabourContractionEndPutResponse = (LabourResponse);

export type CompleteLabourApiV1LabourCompletePutData = {
    requestBody: CompleteLabourRequest;
};

export type CompleteLabourApiV1LabourCompletePutResponse = (LabourResponse);

export type GetActiveLabourApiV1LabourActiveGetResponse = (LabourResponse);

export type GetActiveLabourSummaryApiV1LabourActiveSummaryGetResponse = (LabourSummaryResponse);

export type RegisterApiV1SubscriberRegisterPostData = {
    requestBody: RegisterSubscriberRequest;
};

export type RegisterApiV1SubscriberRegisterPostResponse = (SubscriberResponse);

export type SubscribeToApiV1SubscriberSubscribeToBirthingPersonIdPostData = {
    birthingPersonId: string;
    requestBody: SubscribeToRequest;
};

export type SubscribeToApiV1SubscriberSubscribeToBirthingPersonIdPostResponse = (SubscriberResponse);

export type UnsubscribeFromApiV1SubscriberUnsubscribeFromPostData = {
    requestBody: UnsubscribeFromRequest;
};

export type UnsubscribeFromApiV1SubscriberUnsubscribeFromPostResponse = (SubscriberResponse);

export type GetSubscriptionsApiV1SubscriberSubcriptionsGetResponse = (GetSubscriptionsResponse);