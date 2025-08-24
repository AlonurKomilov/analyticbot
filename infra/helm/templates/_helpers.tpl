{{/*
Expand the name of the chart.
*/}}
{{- define "analyticbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "analyticbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "analyticbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "analyticbot.labels" -}}
helm.sh/chart: {{ include "analyticbot.chart" . }}
{{ include "analyticbot.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "analyticbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "analyticbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "analyticbot.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "analyticbot.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "analyticbot.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
postgresql+asyncpg://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "analyticbot.fullname" . }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- else }}
postgresql+asyncpg://{{ .Values.env.POSTGRES_USER }}:{{ .Values.env.POSTGRES_PASSWORD }}@{{ .Values.env.POSTGRES_HOST }}:{{ .Values.env.POSTGRES_PORT }}/{{ .Values.env.POSTGRES_DB }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "analyticbot.redisUrl" -}}
{{- if .Values.redis.enabled }}
redis://{{ include "analyticbot.fullname" . }}-redis-master:6379/0
{{- else }}
{{ .Values.env.REDIS_URL }}
{{- end }}
{{- end }}
