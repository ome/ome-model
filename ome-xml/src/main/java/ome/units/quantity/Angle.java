/*
 * #%L
 * The OME Data Model specification
 * %%
 * Copyright (C) 2014 - 2016 Open Microscopy Environment:
 *   - Board of Regents of the University of Wisconsin-Madison
 *   - Glencoe Software, Inc.
 *   - University of Dundee
 * %%
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, either version 2 of the
 * License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public
 * License along with this program.  If not, see
 * <http://www.gnu.org/licenses/gpl-2.0.html>.
 * #L%
 */

package ome.units.quantity;

import ome.units.unit.Unit;

/**
 * Angle quantity.
 *
 * @since 5.1
 */
public class Angle extends Quantity implements Comparable<Angle>
{
  /** Seed for hashCode. */
  private static final int SEED1 = 12;
  /** Seed for hashCode. */
  private static final int SEED2 = 23;
  /** Value of this quantity. */
  Number value;
  /** Unit type of this quantity. */
  Unit<ome.units.quantity.Angle> unit;
  /** Cached value for hashCode. */
  private int hashCodeValue;

  /**
   * Create an Angle.
   *
   * @param inValue the value.
   * @param inUnit the unit type.
   */
  public Angle(Number inValue,
    Unit<ome.units.quantity.Angle> inUnit)
  {
    if (inValue == null)
    {
      throw new NullPointerException("Angle: Angle cannot be constructed with a null value.");
    }
    value = inValue;
    unit = inUnit;
    hashCodeValue = SEED1;
    hashCodeValue = SEED2 * hashCodeValue + Float.floatToIntBits(value.floatValue());
    hashCodeValue = SEED2 * hashCodeValue + unit.getSymbol().hashCode();
  }

  @Override
  public Number value()
  {
    return value;
  }

  /**
   * Perform a unit conversion.
   *
   * @param inUnit the unit to convert to.
   * @return the current quantity value converted to the specified
   * unit, or null if the conversion is not possible.
   */
  public Number value(Unit<ome.units.quantity.Angle> inUnit)
  {
    if (unit.equals(inUnit))
    {
      return value;
    }
    if (unit.isConvertible(inUnit))
    {
      return unit.convertValue(value, inUnit);
    }
    return null;
  }

  /**
   * Check quantities for equality.
   *
   * Unit conversion will be performed when required to convert into
   * the unit system of this quantity in order to perform the
   * comparison.
   *
   * Note that floating point comparison is dangerous.  Do not use
   * this method.
   *
   * @return true if equal, false if not equal.
   */
  @Override
  public boolean equals(Object other)
  {
    if (other == null)
    {
      return false;
    }
    if (this.getClass() != other.getClass())
    {
      return false;
    }
    Angle otherAngle = (Angle)other;
    if (unit.equals(otherAngle.unit))
    {
      // Angles use same unit so compare value
      return value.equals(otherAngle.value);
    } else {
      if (unit.isConvertible(otherAngle.unit))
      {
        // Angles use different compatible units so convert value then compare
        return (unit.convertValue(value, otherAngle.unit)).equals(otherAngle.value);
      }
    }
    return false;
  }

  /**
   * Check quantities for equality.
   *
   * Unit conversion will be performed when required to convert into
   * the unit system of this quantity in order to perform the
   * comparison.
   *
   * Note that floating point comparison is dangerous.  Do not use
   * this method.
   *
   * @return true if equal, false if not equal.
   */
  @Override
  public int compareTo(Angle other)
  {
    if (this == other) {
      return 0;
    }
    return Double.compare(value.doubleValue(), other.value(unit).doubleValue());
  }

  @Override
  public int hashCode()
  {
    return hashCodeValue;
  }
  @Override
  public String toString()
  {
    String result = this.getClass().getName() +
            ": " +
            "value[" +
            value +
            "], unit[" +
            unit.getSymbol() +
            "] stored as " +
            value.getClass().getName();
    return result;
  }

  @Override
  public Unit<ome.units.quantity.Angle> unit()
  {
    return unit;
  }
}
