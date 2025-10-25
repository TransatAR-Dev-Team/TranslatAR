declare module 'react-google-button' {
  import { Component } from 'react';

  interface GoogleButtonProps {
    onClick?: () => void;
    label?: string;
    style?: React.CSSProperties;
    className?: string;
    disabled?: boolean;
  }

  export default class GoogleButton extends Component<GoogleButtonProps> {}
}
