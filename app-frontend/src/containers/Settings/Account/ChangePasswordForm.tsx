import React from 'react'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormError,
  FormButton
} from '../../../components/Form'
import Flex from '../../../components/atoms/Flex'
import Container from '../../../components/atoms/Container'

interface RenderFieldProps {
  input: string,
  label: string,
  type: string,
  meta: any,
  touched: boolean,
  error: string,
  initialValues: any
}

interface ChangePasswordFormProps extends InjectedFormProps {
  registering?: boolean
}

const required = (value: string) =>
  value || typeof value === 'string' ? undefined : 'Required'

const minLength = (value: string) =>
  value && value.length < 8 ? `Must be 8 characters or more` : undefined

const matchPassword = (value: string, allValues: any) =>
  value !== allValues.password ? 'Passwords do not match' : undefined

const renderField = ({ input, label, type, meta: { touched, error } }: RenderFieldProps) => (
  <FormField>
    <Flex>
      <FieldLabel py={0} width={1 / 2}>
        {label}
      </FieldLabel>
      <Container width={2 / 3}>
        <FormInput {...input} type={type} placeholder={label} />
        {touched && (error && <FormError>{error}</FormError>)}
      </Container>
    </Flex>
  </FormField>
)

const ChangePasswordForm = (props: ChangePasswordFormProps) => {
  const { handleSubmit, invalid, registering } = props
  return (
    <Form mx={3} width={1 / 2} onSubmit={handleSubmit}>
      <Field
        name="password"
        label="New Password"
        component={renderField}
        type="password"
        validate={[required, minLength]}
      />
      <Field
        name="confirmPassword"
        label="Confirm Password"
        component={renderField}
        type="password"
        validate={[required, matchPassword]}
      />
      <FormButton type="submit" disabled={invalid}>
        {registering ? '...' : 'Submit'}
      </FormButton>
    </Form>
  )
}


export default reduxForm({
  form: 'changePassword'
})(ChangePasswordForm)