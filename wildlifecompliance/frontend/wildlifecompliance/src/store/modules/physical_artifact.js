import Vue from 'vue';
import {
    api_endpoints,
    helpers
}
from '@/utils/hooks';
import moment from 'moment';

export const physicalArtifactStore = {
    namespaced: true,
    state: {
        physical_artifact: {
        },
        
    },
    getters: {
        physical_artifact: (state) => state.physical_artifact,
    },
    mutations: {
        updatePhysicalArtifact(state, physical_artifact) {
            Vue.set(state, 'physical_artifact', {
                ...physical_artifact
            });
            console.log('updatePhysicalArtifact');
            // format artifact_date for vue
            if (state.physical_artifact.artifact_date) {
                state.physical_artifact.artifact_date = moment(state.physical_artifact.artifact_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            // format disposal_date for vue
            if (state.physical_artifact.disposal_date) {
                state.physical_artifact.disposal_date = moment(state.physical_artifact.disposal_date, 'YYYY-MM-DD').format('DD/MM/YYYY');
            }
            // default doc implemented in Artifact model/viewset
            let defaultDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.artifact,
                state.physical_artifact.id + "/process_default_document/"
                )
            Vue.set(state.physical_artifact, 'defaultDocumentUrl', defaultDocumentUrl); 
            // comms log doc implemented in Artifact model/viewset
            let commsLogsDocumentUrl = helpers.add_endpoint_join(
                api_endpoints.artifact,
                state.physical_artifact.id + "/process_comms_log_document/"
                )
            Vue.set(state.physical_artifact, 'commsLogsDocumentUrl', commsLogsDocumentUrl); 
            /*
            let createLegalCaseProcessCommsLogsPhysicalUrl = helpers.add_endpoint_join(
                api_endpoints.legal_case,
                state.legal_case.id + "/create_legal_case_process_comms_log_physical/"
                )
            Vue.set(state.legal_case, 'createLegalCaseProcessCommsLogsPhysicalUrl', createLegalCaseProcessCommsLogsPhysicalUrl);
            */
        },
        updateRelatedItems(state, related_items) {
            Vue.set(state.physical_artifact, 'related_items', related_items);
        },
        updateOfficerEmail(state, email) {
            Vue.set(state.physical_artifact, 'officer_email', email);
        },
        updateTemporaryDocumentCollectionId(state, temp_doc_id) {
            Vue.set(state.physical_artifact, 'temporary_document_collection_id', temp_doc_id);
        },
        /*
        updatePhysicalArtifactLegalId(state, legal_case_id) {
            Vue.set(state.physical_artifact, 'legal_case_id', legal_case_id);
        },
        */
    },
    actions: {
        async loadPhysicalArtifact({ dispatch, commit }, { physical_artifact_id }) {
            try {
                const returnedPhysicalArtifact = await Vue.http.get(
                    helpers.add_endpoint_json(
                        api_endpoints.physical_artifact,
                        physical_artifact_id)
                    );

                console.log(returnedPhysicalArtifact)
                commit("updatePhysicalArtifact", returnedPhysicalArtifact.body);

            } catch (err) {
                console.log(err);
            }
        },
        async savePhysicalArtifact({ dispatch, state, rootGetters }, { create, internal, legal_case_id }) {
            let physicalArtifactId = null;
            let savedPhysicalArtifact = null;
            try {
                let payload = new Object();
                Object.assign(payload, state.physical_artifact);
                console.log(payload);
                // format artifact date for backend save
                if (payload.artifact_date) {
                    payload.artifact_date = moment(payload.artifact_date, 'DD/MM/YYYY').format('YYYY-MM-DD');
                } else if (payload.artifact_date === '') {
                    payload.artifact_date = null;
                }
                // format disposal date for backend save
                if (payload.disposal_date) {
                    payload.disposal_date = moment(payload.disposal_date, 'DD/MM/YYYY').format('YYYY-MM-DD');
                } else if (payload.disposal_date === '') {
                    payload.disposal_date = null;
                }
                if (legal_case_id) {
                    payload.legal_case_id = legal_case_id;
                }

                let fetchUrl = null;
                if (create) {
                    fetchUrl = api_endpoints.physical_artifact;
                    savedPhysicalArtifact = await Vue.http.post(fetchUrl, payload);
                } else {
                    fetchUrl = helpers.add_endpoint_join(
                        api_endpoints.physical_artifact,
                        state.physical_artifact.id + '/'
                        )
                    console.log(payload);
                    savedPhysicalArtifact = await Vue.http.put(fetchUrl, payload);
                }
                await dispatch("setPhysicalArtifact", savedPhysicalArtifact.body);
                physicalArtifactId = savedPhysicalArtifact.body.id;

            } catch (err) {
                console.log(err);
                if (internal) {
                    // return "There was an error saving the record";
                    return err;
                } else {
                    await swal("Error", "There was an error saving the record", "error");
                }
            }
            // internal arg used when file upload triggers record creation
            if (internal) {
                // pass
            }
            // update legal_case
            else if (!create) {
                await swal("Saved", "The record has been saved", "success");
            }
        },
        setPhysicalArtifact({ commit, }, physical_artifact) {
            commit("updatePhysicalArtifact", physical_artifact);
        },
        /*
        setPhysicalArtifactLegalId({ commit, }, legal_case_id) {
            commit("updatePhysicalArtifactLegalId", legal_case_id)
        },
        */
        setRelatedItems({ commit }, related_items ) {
            commit("updateRelatedItems", related_items);
        },
        setOfficerEmail({ commit }, email ) {
            commit("updateOfficerEmail", email);
        },
        setTemporaryDocumentCollectionId({ commit }, temp_doc_id) {
            commit("updateTemporaryDocumentCollectionId", temp_doc_id);
        },
    },
};